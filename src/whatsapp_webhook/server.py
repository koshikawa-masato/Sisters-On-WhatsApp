"""FastAPI webhook server for WhatsApp (Twilio)."""

import os
from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import logging

from ..config import Config
from ..llm.factory import LLMFactory
from ..llm.base import Message
from ..characters.personality import CharacterPersonality
from ..routing.topic_analyzer import TopicAnalyzer
from ..session.manager import SessionManager
from ..moderation.openai_moderator import OpenAIModerator

# Load environment variables from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

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
# session_manager = SessionManager()  # Disabled for testing without PostgreSQL
session_manager = SimpleSession()  # Use in-memory session for testing
moderator = OpenAIModerator()

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

        # Step 1: Content moderation
        moderation_result = await moderator.moderate(Body)

        if moderation_result.should_block():
            logger.warning(f"Blocked message from {phone_number}: {moderation_result.blocked_reason}")
            twiml_response.message(Config.MODERATION_BLOCKED_MESSAGE)
            return Response(content=str(twiml_response), media_type="application/xml")

        # Step 2: Get or create user session
        user_session = session_manager.get_or_create_session(phone_number)
        current_character = user_session.current_character

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

        # Step 5: Load character personality
        system_prompt = character_loader.get_system_prompt(selected_character)

        # Step 6: Get conversation history
        history = session_manager.get_conversation_history(
            phone_number,
            character=selected_character,
            limit=Config.CONVERSATION_HISTORY_LIMIT
        )

        # Step 7: Build messages for LLM
        messages = [Message(role="system", content=system_prompt)]

        # Add conversation history
        for msg in history:
            messages.append(Message(role=msg["role"], content=msg["content"]))

        # Add current user message
        messages.append(Message(role="user", content=Body))

        # Step 8: Generate response
        response_text = await llm_provider.generate(
            messages,
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS
        )

        logger.info(f"Generated response ({selected_character}): {response_text[:100]}...")

        # Step 9: Save conversation to history
        session_manager.add_message(phone_number, selected_character, "user", Body)
        session_manager.add_message(phone_number, selected_character, "assistant", response_text)

        # Step 10: Send response via Twilio (with character name and emoji)
        character_emoji = CHARACTER_EMOJIS.get(selected_character, '')
        formatted_response = f"*{selected_character.capitalize()}{character_emoji}*: {response_text}"
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
