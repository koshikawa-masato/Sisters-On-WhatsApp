"""LLM provider factory."""

import os
from typing import Optional
from .base import LLMProvider
from .kimi_provider import KimiProvider
from .openai_provider import OpenAIProvider


class LLMFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create_provider(
        provider_type: Optional[str] = None,
        model: Optional[str] = None,
    ) -> LLMProvider:
        """
        Create an LLM provider based on environment configuration.

        Args:
            provider_type: Override provider type (kimi, openai)
            model: Override model name

        Returns:
            Configured LLM provider instance
        """
        if provider_type is None:
            provider_type = os.getenv("PRIMARY_LLM")
            if not provider_type:
                raise ValueError("PRIMARY_LLM not found in environment")
            provider_type = provider_type.lower()

        if provider_type == "kimi":
            api_key = os.getenv("KIMI_API_KEY")
            if not api_key:
                raise ValueError("KIMI_API_KEY not found in environment")

            if model is None:
                model = os.getenv("KIMI_MODEL")
                if not model:
                    raise ValueError("KIMI_MODEL not found in environment")

            return KimiProvider(api_key=api_key, model=model)

        elif provider_type == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            if model is None:
                model = os.getenv("OPENAI_MODEL")
                if not model:
                    raise ValueError("OPENAI_MODEL not found in environment")

            return OpenAIProvider(api_key=api_key, model=model)

        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
