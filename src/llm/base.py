"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Message:
    """Chat message structure."""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name for logging."""
        pass
