"""FastAPI webhook server for WhatsApp (Twilio)."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables BEFORE importing config
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import logging

from ..config import Config
from ..llm.factory import LLMFactory
from ..llm.base import Message
from ..characters.personality import CharacterPersonality
from ..routing.topic_analyzer import TopicAnalyzer
from ..session.manager import SessionManager
from ..moderation.openai_moderator import OpenAIModerator
from ..utils.language_detector import detect_language, get_language_instruction
from ..utils.admin_notifier import AdminNotifier
from ..memory.conversation_learner import ConversationLearner
from ..privacy.consent_manager import ConsentManager
from ..privacy.policy_messages import PrivacyPolicyMessages, Region
from ..privacy.data_manager import DataManager

# Validate configuration
Config.validate()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Sisters-On-WhatsApp", version="1.0.0")

# Simple in-memory session for testing without database
class SimpleSession:
    def __init__(self):
        self.sessions = {}  # phone_number -> {"current_character": str, "history": []}

    def get_or_create_session(self, phone_number):
        if phone_number not in self.sessions:
            self.sessions[phone_number] = type('Session', (), {
                'current_character': 'botan',
                'history': []
            })()
        return self.sessions[phone_number]

    def update_character(self, phone_number, character):
        if phone_number in self.sessions:
            self.sessions[phone_number].current_character = character

    def get_conversation_history(self, phone_number, limit=10, character=None):
        if phone_number in self.sessions:
            return self.sessions[phone_number].history[-limit:]
        return []

    def add_message(self, phone_number, character, role, content):
        if phone_number in self.sessions:
            self.sessions[phone_number].history.append({"role": role, "content": content})

# Initialize components
llm_provider = LLMFactory.create_provider()
character_loader = CharacterPersonality()
topic_analyzer = TopicAnalyzer()
session_manager = SessionManager()  # PostgreSQL persistent sessions enabled
# session_manager = SimpleSession()  # In-memory sessions (testing only)
moderator = OpenAIModerator()
conversation_learner = ConversationLearner()
admin_notifier = AdminNotifier()
consent_manager = ConsentManager()
data_manager = DataManager()

# Ensure privacy tables exist
try:
    consent_manager.ensure_table_exists()
    logger.info("Privacy tables initialized")
except Exception as e:
    logger.warning(f"Privacy table initialization failed (will retry on first use): {e}")

# Character emoji icons
CHARACTER_EMOJIS = {
    'botan': '🌸',
    'kasho': '🎵',
    'yuri': '📚'
}

logger.info(f"LLM Provider: {llm_provider.get_provider_name()}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Sisters-On-WhatsApp",
        "llm": llm_provider.get_provider_name()
    }


@app.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(None),
    MessageSid: str = Form(None)
):
    """
    Handle incoming WhatsApp messages from Twilio.

    Args:
        Body: Message content
        From: Sender's phone number (format: whatsapp:+1234567890)
        To: Recipient's phone number
        MessageSid: Message ID from Twilio
    """
    logger.info(f"Received message from {From}: {Body}")

    # Create Twilio response
    twiml_response = MessagingResponse()

    try:
        # Extract phone number (remove "whatsapp:" prefix)
        phone_number = From.replace("whatsapp:", "")

        # Detect language early for privacy messages
        detected_language = detect_language(Body)

        # Step 0: Check for privacy commands (DELETE, EXPORT) - always allowed
        consent_command = PrivacyPolicyMessages.is_consent_command(Body)

        if consent_command == "delete":
            # Handle data deletion request
            data_manager.delete_user_data(phone_number, reason="user_request")
            response_msg = PrivacyPolicyMessages.get_response("data_deleted", detected_language)
            twiml_response.message(response_msg)
            logger.info(f"Data deleted for {phone_number[:6]}... (user request)")
            return Response(content=str(twiml_response), media_type="application/xml")

        if consent_command == "export":
            # Handle data export request
            data_manager.export_user_data(phone_number)
            response_msg = PrivacyPolicyMessages.get_response("data_exported", detected_language)
            twiml_response.message(response_msg)
            logger.info(f"Data export requested for {phone_number[:6]}...")
            return Response(content=str(twiml_response), media_type="application/xml")

        if consent_command == "privacy":
            # Show privacy policy info with region-specific URL
            response_msg = PrivacyPolicyMessages.get_privacy_info(phone_number, detected_language)
            twiml_response.message(response_msg)
            logger.info(f"Privacy info requested by {phone_number[:6]}...")
            return Response(content=str(twiml_response), media_type="application/xml")

        if consent_command == "help":
            # Show available commands
            response_msg = PrivacyPolicyMessages.get_response("help_info", detected_language)
            twiml_response.message(response_msg)
            logger.info(f"Help info requested by {phone_number[:6]}...")
            return Response(content=str(twiml_response), media_type="application/xml")

        # Step 0.5: Check consent status (implicit consent model)
        user_consent = consent_manager.get_user_consent(phone_number)

        if not user_consent:
            # New user - grant implicit consent and continue to chat
            consent_manager.create_pending_consent(phone_number, detected_language)
            consent_manager.grant_consent(phone_number)
            logger.info(f"Implicit consent granted for new user {phone_number[:6]}...")
            # Continue to normal flow - don't return, let them chat immediately

        elif user_consent["status"] == "pending":
            # Legacy pending user - grant consent now
            consent_manager.grant_consent(phone_number)
            logger.info(f"Consent auto-granted for pending user {phone_number[:6]}...")

        elif user_consent["status"] in ["declined", "withdrawn"]:
            # User previously opted out - re-grant consent (they're messaging again)
            consent_manager.grant_consent(phone_number)
            logger.info(f"Consent re-granted for returning user {phone_number[:6]}...")

        # At this point, user has valid consent - continue to chat

        # Step 1: Content moderation
        moderation_result = await moderator.moderate(Body)

        if moderation_result.should_block():
            logger.warning(f"Blocked message from {phone_number}: {moderation_result.blocked_reason}")
            twiml_response.message(Config.MODERATION_BLOCKED_MESSAGE)
            return Response(content=str(twiml_response), media_type="application/xml")

        # Step 2: Get or create user session
        user_session = session_manager.get_or_create_session(phone_number)
        current_character = user_session.current_character

        # Check if this is the first message (empty history)
        history = session_manager.get_conversation_history(phone_number, limit=1)
        is_first_message = len(history) == 0

        if is_first_message:
            # Detect language for welcome message
            language = detect_language(Body)

            # Get region-specific privacy URL
            region = PrivacyPolicyMessages.detect_region(phone_number)
            policy_url = PrivacyPolicyMessages.POLICY_URLS.get(region, PrivacyPolicyMessages.POLICY_URLS[Region.DEFAULT])

            # Short, natural welcome message with embedded privacy info
            if language == 'zh':
                welcome_message = (
                    "嗨！👋 我是Botan，三姐妹AI之一～\n\n"
                    "🌸 我 - VTuber、直播\n"
                    "🎵 Kasho姐 - 音樂、人生相談\n"
                    "📚 Yuri妹 - 書籍、創作\n\n"
                    "隨便問什麼，對的姐妹會回答你！\n\n"
                    f"ℹ️ 對話會被保存。詳情：{policy_url}\n"
                    "想刪除？說「刪除我的資料」就OK～"
                )
            else:
                welcome_message = (
                    "Hey! 👋 I'm Botan, one of three AI sisters~\n\n"
                    "🌸 Me - VTubers, streaming\n"
                    "🎵 Kasho sis - Music, life advice\n"
                    "📚 Yuri sis - Books, writing\n\n"
                    "Ask anything and the right sister will answer!\n\n"
                    f"ℹ️ Chats are saved. Details: {policy_url}\n"
                    "Want to delete? Just say \"delete my data\"~"
                )

            twiml_response.message(welcome_message)

            # Save welcome message to history to prevent re-sending
            session_manager.add_message(
                phone_number=phone_number,
                character="botan",
                role="assistant",
                content=welcome_message
            )
            session_manager.add_message(
                phone_number=phone_number,
                character="botan",
                role="user",
                content=Body
            )

            # Notify admin about new user
            admin_notifier.send_new_user_notification(phone_number, Body)

            return Response(content=str(twiml_response), media_type="application/xml")

        # Step 3: Topic analysis & character routing
        selected_character, topic_scores = topic_analyzer.select_character(
            Body,
            current_character=current_character,
            threshold=Config.CHARACTER_SWITCH_THRESHOLD
        )

        logger.info(
            f"Topic scores: {topic_scores} | "
            f"Current: {current_character} | Selected: {selected_character}"
        )

        # Step 4: Update character if switched
        if selected_character != current_character:
            session_manager.update_character(phone_number, selected_character)
            logger.info(f"Character switched: {current_character} -> {selected_character}")

        # Step 5: Detect language
        language = detect_language(Body)
        language_instruction = get_language_instruction(language)
        logger.info(f"Detected language: {language}")

        # Step 6: Load character personality with language instruction and verified knowledge
        system_prompt = character_loader.get_system_prompt(selected_character, user_message=Body)
        system_prompt += language_instruction

        # Step 7: Get conversation history
        history = session_manager.get_conversation_history(
            phone_number,
            character=selected_character,
            limit=Config.CONVERSATION_HISTORY_LIMIT
        )

        # Step 8: Build messages for LLM
        messages = [Message(role="system", content=system_prompt)]

        # Add conversation history
        for msg in history:
            messages.append(Message(role=msg["role"], content=msg["content"]))

        # Add current user message
        messages.append(Message(role="user", content=Body))

        # Step 9: Generate response (with automatic failover)
        try:
            response_text = await llm_provider.generate(
                messages,
                temperature=Config.LLM_TEMPERATURE,
                max_tokens=Config.LLM_MAX_TOKENS
            )
            logger.info(f"Generated response ({selected_character}): {response_text[:100]}...")
        except Exception as primary_error:
            # Primary LLM failed, try failover to secondary LLM
            logger.warning(f"Primary LLM ({Config.PRIMARY_LLM}) failed: {str(primary_error)}")

            # Determine failover LLM (opposite of primary)
            failover_llm = "openai" if Config.PRIMARY_LLM == "kimi" else "kimi"
            logger.info(f"Attempting failover to {failover_llm}...")

            try:
                # Create failover provider
                failover_provider = LLMFactory.create_provider(provider_type=failover_llm)
                response_text = await failover_provider.generate(
                    messages,
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=Config.LLM_MAX_TOKENS
                )
                logger.info(f"✅ Failover successful! Generated response with {failover_llm}: {response_text[:100]}...")
            except Exception as failover_error:
                # Both LLMs failed
                logger.error(f"❌ Failover to {failover_llm} also failed: {str(failover_error)}")
                raise Exception(f"All LLM providers failed. Primary: {str(primary_error)}, Failover: {str(failover_error)}")

        # Step 9: Save conversation to history
        session_manager.add_message(phone_number, selected_character, "user", Body)
        session_manager.add_message(phone_number, selected_character, "assistant", response_text)

        # Step 9.5: Check if user is providing a correction (learning from conversation)
        conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-3:]])
        correction_detected = conversation_learner.process_message(
            user_message=Body,
            phone_number=phone_number,
            conversation_context=conversation_context
        )

        if correction_detected:
            logger.info(
                f"✅ User correction detected: {correction_detected['extracted_fact']} "
                f"(confidence: {correction_detected['confidence']:.0%})"
            )

            # Notify admin about detected correction
            admin_notifier.send_correction_notification(
                user_phone=phone_number,
                extracted_fact=correction_detected['extracted_fact'],
                category=correction_detected['category'],
                confidence=correction_detected['confidence'],
                original_message=Body
            )

        # Step 9.6: Check if user asked about privacy/data handling
        privacy_keywords = [
            "privacy", "隱私", "隐私", "data", "資料", "数据",
            "personal information", "個人資訊", "个人信息",
            "how do you use", "what do you collect", "my information",
            "delete my", "erase my", "remove my",
            "你們怎麼用", "收集什麼", "我的資料", "刪除我的"
        ]
        is_privacy_question = any(kw in Body.lower() for kw in privacy_keywords)

        # Step 10: Send response via Twilio (with character name and emoji)
        character_emoji = CHARACTER_EMOJIS.get(selected_character, '')
        formatted_response = f"*{selected_character.capitalize()}{character_emoji}*: {response_text}"

        # Append privacy URL if user asked about privacy
        if is_privacy_question:
            region = PrivacyPolicyMessages.detect_region(phone_number)
            policy_url = PrivacyPolicyMessages.POLICY_URLS.get(region, PrivacyPolicyMessages.POLICY_URLS[Region.DEFAULT])
            if language == 'zh':
                formatted_response += f"\n\n📋 完整隱私政策：{policy_url}"
            else:
                formatted_response += f"\n\n📋 Full privacy policy: {policy_url}"

        twiml_response.message(formatted_response)

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        twiml_response.message(Config.ERROR_MESSAGE)

    return Response(content=str(twiml_response), media_type="application/xml")


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "components": {
            "llm": llm_provider.get_provider_name(),
            "characters": character_loader.ALL_CHARACTERS,
            "database": "connected"  # TODO: Add actual DB health check
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.SERVER_HOST, port=Config.SERVER_PORT)
