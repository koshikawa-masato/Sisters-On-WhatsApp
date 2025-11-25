"""Session management for user conversations."""

import os
import logging
from typing import Optional, List, Dict
from urllib.parse import quote_plus
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from .models import Base, UserSession, ConversationHistory
from ..privacy.encryption import ConversationEncryption

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage user sessions and conversation history."""

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize session manager.

        Args:
            database_url: PostgreSQL connection string (default from env)
        """
        if database_url is None:
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "sisters_on_whatsapp")
            user = os.getenv("POSTGRES_USER", "postgres")
            password = os.getenv("POSTGRES_PASSWORD", "")

            # URL-encode password to handle special characters (like !)
            encoded_password = quote_plus(password) if password else ""
            database_url = f"postgresql://{user}:{encoded_password}@{host}:{port}/{db}"

        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Initialize encryption
        self.encryption = ConversationEncryption()

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    def get_or_create_session(self, phone_number: str) -> UserSession:
        """Get existing session or create new one."""
        phone_hash = self.encryption.hash_phone_number(phone_number)

        with self.SessionLocal() as db:
            # First try to find by hash (new encrypted records)
            session = db.query(UserSession).filter(
                UserSession.phone_hash == phone_hash
            ).first()

            # Fallback: try to find by plain phone number (legacy records)
            if not session:
                session = db.query(UserSession).filter(
                    UserSession.phone_number == phone_number,
                    UserSession.phone_hash.is_(None)
                ).first()

                # Migrate legacy record if found
                if session:
                    session.phone_hash = phone_hash
                    session.phone_number = self.encryption.encrypt(phone_number)
                    db.commit()
                    logger.info(f"Migrated legacy session for phone hash {phone_hash[:8]}...")

            if not session:
                # Create new encrypted session
                session = UserSession(
                    phone_hash=phone_hash,
                    phone_number=self.encryption.encrypt(phone_number),
                    current_character="botan"  # Default to Botan
                )
                db.add(session)
                db.commit()
                db.refresh(session)

            return session

    def update_character(self, phone_number: str, character: str) -> None:
        """Update the current character for a user."""
        phone_hash = self.encryption.hash_phone_number(phone_number)

        with self.SessionLocal() as db:
            # Find by hash first, then fallback to plain phone number
            session = db.query(UserSession).filter(
                UserSession.phone_hash == phone_hash
            ).first()

            if not session:
                session = db.query(UserSession).filter(
                    UserSession.phone_number == phone_number
                ).first()

            if session:
                session.current_character = character
                session.last_interaction = datetime.utcnow()
                db.commit()

    def get_current_character(self, phone_number: str) -> str:
        """Get current character for a user."""
        session = self.get_or_create_session(phone_number)
        return session.current_character

    def add_message(
        self,
        phone_number: str,
        character: str,
        role: str,
        content: str
    ) -> None:
        """Add a message to conversation history (encrypted)."""
        phone_hash = self.encryption.hash_phone_number(phone_number)
        encrypted_phone = self.encryption.encrypt(phone_number)
        encrypted_content = self.encryption.encrypt(content)

        with self.SessionLocal() as db:
            message = ConversationHistory(
                phone_hash=phone_hash,
                phone_number=encrypted_phone,
                character=character,
                role=role,
                content=encrypted_content
            )
            db.add(message)
            db.commit()

    def get_conversation_history(
        self,
        phone_number: str,
        character: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """
        Get recent conversation history (decrypted).

        Args:
            phone_number: User's phone number
            character: Filter by character (optional)
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages in format [{"role": "user", "content": "..."}]
        """
        phone_hash = self.encryption.hash_phone_number(phone_number)

        with self.SessionLocal() as db:
            # Try to find by hash first (new encrypted records)
            query = db.query(ConversationHistory).filter(
                ConversationHistory.phone_hash == phone_hash
            )

            if character:
                query = query.filter(ConversationHistory.character == character)

            messages = query.order_by(
                desc(ConversationHistory.timestamp)
            ).limit(limit).all()

            # If no messages found by hash, try legacy plain phone number
            if not messages:
                query = db.query(ConversationHistory).filter(
                    ConversationHistory.phone_number == phone_number,
                    ConversationHistory.phone_hash.is_(None)
                )
                if character:
                    query = query.filter(ConversationHistory.character == character)

                messages = query.order_by(
                    desc(ConversationHistory.timestamp)
                ).limit(limit).all()

            # Reverse to get chronological order
            messages.reverse()

            # Decrypt content
            result = []
            for msg in messages:
                content = msg.content
                # Decrypt if encrypted (check if it looks like encrypted data)
                if self.encryption.is_encrypted(content):
                    content = self.encryption.decrypt(content)
                result.append({"role": msg.role, "content": content})

            return result

    def clear_old_history(self, days: int = 30) -> int:
        """
        Clear conversation history older than specified days.

        Args:
            days: Number of days to keep

        Returns:
            Number of deleted records
        """
        with self.SessionLocal() as db:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = db.query(ConversationHistory).filter(
                ConversationHistory.timestamp < cutoff_date
            ).delete()
            db.commit()
            return deleted
