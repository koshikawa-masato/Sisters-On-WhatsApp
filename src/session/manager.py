"""Session management for user conversations."""

import os
from typing import Optional, List, Dict
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta
from .models import Base, UserSession, ConversationHistory


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

            database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)

    def get_or_create_session(self, phone_number: str) -> UserSession:
        """Get existing session or create new one."""
        with self.SessionLocal() as db:
            session = db.query(UserSession).filter(
                UserSession.phone_number == phone_number
            ).first()

            if not session:
                session = UserSession(
                    phone_number=phone_number,
                    current_character="botan"  # Default to Botan
                )
                db.add(session)
                db.commit()
                db.refresh(session)

            return session

    def update_character(self, phone_number: str, character: str) -> None:
        """Update the current character for a user."""
        with self.SessionLocal() as db:
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
        """Add a message to conversation history."""
        with self.SessionLocal() as db:
            message = ConversationHistory(
                phone_number=phone_number,
                character=character,
                role=role,
                content=content
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
        Get recent conversation history.

        Args:
            phone_number: User's phone number
            character: Filter by character (optional)
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages in format [{"role": "user", "content": "..."}]
        """
        with self.SessionLocal() as db:
            query = db.query(ConversationHistory).filter(
                ConversationHistory.phone_number == phone_number
            )

            if character:
                query = query.filter(ConversationHistory.character == character)

            messages = query.order_by(
                desc(ConversationHistory.timestamp)
            ).limit(limit).all()

            # Reverse to get chronological order
            messages.reverse()

            return [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

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
