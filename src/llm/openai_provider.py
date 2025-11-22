"""OpenAI LLM provider (backup/fallback)."""

from typing import List, Optional
from openai import AsyncOpenAI
from .base import LLMProvider, Message


class OpenAIProvider(LLMProvider):
    """OpenAI GPT implementation."""

    def __init__(self, api_key: str, model: str):
        super().__init__(api_key, model)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate response using OpenAI API."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[msg.to_dict() for msg in messages],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def get_provider_name(self) -> str:
        return f"OpenAI ({self.model})"
