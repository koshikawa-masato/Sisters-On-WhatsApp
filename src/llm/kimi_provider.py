"""Kimi (Moonshot AI) LLM provider."""

import httpx
from typing import List, Optional
from .base import LLMProvider, Message


class KimiProvider(LLMProvider):
    """Kimi (Moonshot AI) implementation."""

    API_BASE_URL = "https://api.moonshot.cn/v1"

    def __init__(self, api_key: str, model: str = "moonshot-v1-8k"):
        super().__init__(api_key, model)

    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate response using Kimi API."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.API_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

    def get_provider_name(self) -> str:
        return f"Kimi ({self.model})"
