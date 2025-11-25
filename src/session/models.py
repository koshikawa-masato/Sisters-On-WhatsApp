"""Database models for session management."""

from sqlalchemy import Column, String, DateTime, Text, Integer, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class UserSession(Base):
    """User conversation session tracking."""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_hash = Column(String(64), nullable=True, index=True, unique=True)  # SHA-256 hash for lookup
    phone_number = Column(String(255), nullable=False)  # Encrypted phone number
    current_character = Column(String(20), nullable=False, default="botan")
    last_interaction = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<UserSession(phone={self.phone_number}, character={self.current_character})>"


class ConversationHistory(Base):
    """Store conversation history for context."""

    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_hash = Column(String(64), nullable=True, index=True)  # SHA-256 hash for lookup
    phone_number = Column(String(255), nullable=False)  # Encrypted phone number
    character = Column(String(20), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)  # Encrypted content
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ConversationHistory(phone={self.phone_number}, role={self.role})>"
