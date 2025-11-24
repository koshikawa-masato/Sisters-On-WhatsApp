"""Admin notification utility for sending feedback to admin via WhatsApp."""

import logging
from typing import Optional
from twilio.rest import Client
from ..config import Config

logger = logging.getLogger(__name__)


class AdminNotifier:
    """Send notifications to admin via WhatsApp."""

    def __init__(self):
        """Initialize Twilio client for admin notifications."""
        self.enabled = Config.ENABLE_ADMIN_NOTIFICATIONS and Config.ADMIN_PHONE_NUMBER

        if self.enabled:
            self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
            self.from_number = Config.TWILIO_WHATSAPP_NUMBER
            self.admin_number = f"whatsapp:{Config.ADMIN_PHONE_NUMBER}"
            logger.info(f"Admin notifications enabled: {Config.ADMIN_PHONE_NUMBER}")
        else:
            self.client = None
            logger.info("Admin notifications disabled")

    def send_correction_notification(
        self,
        user_phone: str,
        extracted_fact: str,
        category: str,
        confidence: float,
        original_message: str
    ) -> bool:
        """
        Send notification when user correction is detected.

        Args:
            user_phone: User's phone number (anonymized last 4 digits shown)
            extracted_fact: The fact extracted from correction
            category: Fact category (place, person, etc.)
            confidence: Confidence score (0-1)
            original_message: User's original message

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Anonymize user phone (show only last 4 digits)
            anonymized_phone = "***" + user_phone[-4:] if len(user_phone) >= 4 else "****"

            # Format notification message
            message = (
                f"🧠 *Learning System Alert*\n\n"
                f"✅ User correction detected!\n\n"
                f"*Fact*: {extracted_fact}\n"
                f"*Category*: {category}\n"
                f"*Confidence*: {confidence:.0%}\n"
                f"*From*: User ending ...{anonymized_phone}\n\n"
                f"*Original Message*:\n\"{original_message}\"\n\n"
                f"📝 Stored in pending_facts.json\n"
                f"🔍 Run fact-check: `python scripts/grok_factcheck.py --auto`"
            )

            # Send via Twilio
            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.admin_number
            )

            logger.info(f"✅ Admin notification sent: {extracted_fact}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send admin notification: {e}")
            return False

    def send_new_user_notification(self, user_phone: str, first_message: str) -> bool:
        """
        Send notification when new user starts conversation.

        Args:
            user_phone: User's phone number (anonymized)
            first_message: User's first message

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Anonymize user phone
            anonymized_phone = "***" + user_phone[-4:] if len(user_phone) >= 4 else "****"

            message = (
                f"👋 *New User Alert*\n\n"
                f"A new user started conversation!\n\n"
                f"*Phone*: ...{anonymized_phone}\n"
                f"*First Message*:\n\"{first_message[:100]}{'...' if len(first_message) > 100 else ''}\"\n\n"
                f"🌸 Welcome message sent by Botan"
            )

            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.admin_number
            )

            logger.info(f"✅ New user notification sent")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send new user notification: {e}")
            return False

    def send_character_switch_notification(
        self,
        user_phone: str,
        from_character: str,
        to_character: str,
        user_message: str,
        topic_scores: dict
    ) -> bool:
        """
        Send notification when character switches (optional, can be noisy).

        Args:
            user_phone: User's phone number (anonymized)
            from_character: Previous character
            to_character: New character
            user_message: User's message that triggered switch
            topic_scores: Topic analysis scores

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Anonymize user phone
            anonymized_phone = "***" + user_phone[-4:] if len(user_phone) >= 4 else "****"

            # Format scores
            scores_text = ", ".join([f"{char}: {score:.2f}" for char, score in topic_scores.items()])

            message = (
                f"🔄 *Character Switch*\n\n"
                f"*User*: ...{anonymized_phone}\n"
                f"*Switch*: {from_character.capitalize()} → {to_character.capitalize()}\n\n"
                f"*Message*:\n\"{user_message[:80]}{'...' if len(user_message) > 80 else ''}\"\n\n"
                f"*Scores*: {scores_text}"
            )

            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.admin_number
            )

            logger.info(f"✅ Character switch notification sent")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send character switch notification: {e}")
            return False

    def send_error_notification(self, error_type: str, error_details: str) -> bool:
        """
        Send notification when critical error occurs.

        Args:
            error_type: Type of error (e.g., "LLM Failure", "Database Error")
            error_details: Error details

        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self.enabled:
            return False

        try:
            message = (
                f"🚨 *System Error Alert*\n\n"
                f"*Type*: {error_type}\n\n"
                f"*Details*:\n{error_details[:200]}{'...' if len(error_details) > 200 else ''}\n\n"
                f"⚠️ Check server logs for full details"
            )

            self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.admin_number
            )

            logger.info(f"✅ Error notification sent")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send error notification: {e}")
            return False
