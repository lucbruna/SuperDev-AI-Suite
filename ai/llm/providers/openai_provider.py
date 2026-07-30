from __future__ import annotations

from typing import Any, AsyncIterator

from .base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, model: str = "gpt-4", api_key: str = "") -> None:
        super().__init__(name="openai", model=model)
        self._api_key = api_key

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return {
            "content": f"OpenAI ({self._model}) response to: {prompt[:50]}...",
            "success": True,
            "tokens_prompt": len(prompt) // 4,
            "tokens_completion": 128,
            "finish_reason": "stop",
            "cost_usd": 0.002,
        }

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        content = f"OpenAI ({self._model}) streaming response"
        words = content.split()
        for i, word in enumerate(words):
            yield {"content": word + " ", "finish_reason": "continue" if i < len(words) - 1 else "stop"}

    async def validate(self, params: dict[str, Any]) -> bool:
        return "max_tokens" in params or True

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_key_set"] = bool(self._api_key)
        return base
