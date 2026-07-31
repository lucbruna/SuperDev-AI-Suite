from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from .base_provider import BaseLLMProvider

_DEFAULT_RESPONSE = (
    "This is a mock response for testing purposes. "
    "It simulates an LLM completion with realistic length."
)


class MockProvider(BaseLLMProvider):
    """Mock provider for testing. Returns canned responses."""

    def __init__(self, response_text: str = "") -> None:
        super().__init__(name="mock", model="mock-model")
        self._response = response_text or _DEFAULT_RESPONSE
        self._call_count = 0

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        self._call_count += 1
        completion_tokens = len(self._response) // 4
        return {
            "content": self._response,
            "success": True,
            "tokens_prompt": len(prompt) // 4,
            "tokens_completion": completion_tokens,
            "finish_reason": "stop",
            "cost_usd": 0.0,
            "call_count": self._call_count,
        }

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _gen() -> AsyncIterator[dict[str, Any]]:
            words = self._response.split()
            for i, word in enumerate(words):
                yield {"content": word + " ", "finish_reason": "continue" if i < len(words) - 1 else "stop"}
        return _gen()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    def set_response(self, text: str) -> None:
        self._response = text

    @property
    def call_count(self) -> int:
        return self._call_count

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["call_count"] = self._call_count
        base["response_preview"] = self._response[:50]
        return base
