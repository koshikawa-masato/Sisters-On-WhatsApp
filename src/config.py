"""Configuration settings for Sisters-On-WhatsApp."""

import os
from typing import Optional


class Config:
    """Application configuration."""

    # Server settings
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Twilio settings
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

    # LLM settings
    PRIMARY_LLM: str = os.getenv("PRIMARY_LLM", "kimi")
    KIMI_API_KEY: Optional[str] = os.getenv("KIMI_API_KEY")
    KIMI_MODEL: str = os.getenv("KIMI_MODEL", "kimi-k2-turbo-preview")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Grok settings (for trend research & fact-checking)
    XAI_API_KEY: Optional[str] = os.getenv("XAI_API_KEY")
    GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-4-fast")
    GROK_ENABLED: bool = os.getenv("GROK_ENABLED", "true").lower() == "true"

    # Database settings
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "sisters_on_whatsapp")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")

    # Character routing settings
    CHARACTER_SWITCH_THRESHOLD: float = float(os.getenv("CHARACTER_SWITCH_THRESHOLD", "0.3"))
    CONVERSATION_HISTORY_LIMIT: int = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "10"))

    # LLM generation settings
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.8"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "500"))

    # Content moderation
    MODERATION_STRICT_MODE: bool = os.getenv("MODERATION_STRICT_MODE", "true").lower() == "true"

    # Response messages (configurable for localization/customization)
    MODERATION_BLOCKED_MESSAGE: str = os.getenv(
        "MODERATION_BLOCKED_MESSAGE",
        "I'm sorry, but I can't respond to that message as it violates our content policy. "
        "Let's talk about something else! 😊"
    )

    ERROR_MESSAGE: str = os.getenv(
        "ERROR_MESSAGE",
        "Oops! Something went wrong on my end. Can you try again? 😅"
    )

    @classmethod
    def get_database_url(cls) -> str:
        """Construct PostgreSQL connection URL."""
        return (
            f"postgresql://{cls.POSTGRES_USER}:{cls.POSTGRES_PASSWORD}"
            f"@{cls.POSTGRES_HOST}:{cls.POSTGRES_PORT}/{cls.POSTGRES_DB}"
        )

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        required = []

        if not cls.KIMI_API_KEY and not cls.OPENAI_API_KEY:
            required.append("At least one LLM API key (KIMI_API_KEY or OPENAI_API_KEY)")

        if not cls.OPENAI_API_KEY:
            required.append("OPENAI_API_KEY (required for content moderation)")

        if required:
            raise ValueError(
                f"Missing required configuration:\n" + "\n".join(f"- {r}" for r in required)
            )
