from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from typing import Any

from .base_provider import BaseLLMProvider


class CustomProvider(BaseLLMProvider):
    """User-configurable custom provider."""

    def __init__(
        self,
        name: str = "custom",
        model: str = "custom-model",
        generate_fn: Callable[..., Any] | None = None,
    ) -> None:
        super().__init__(name=name, model=model)
        self._generate_fn = generate_fn

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        if self._generate_fn:
            result = self._generate_fn(prompt, **kwargs)
            if hasattr(result, "__await__"):
                result = await result
            if isinstance(result, dict):
                return result
        return {
            "content": f"Custom ({self._model}) response to: {prompt[:50]}...",
            "success": True,
            "tokens_prompt": len(prompt) // 4,
            "tokens_completion": 64,
            "finish_reason": "stop",
            "cost_usd": 0.0,
        }

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _gen() -> AsyncIterator[dict[str, Any]]:
            yield {"content": f"Custom ({self._model}) streaming...", "finish_reason": "stop"}

        return _gen()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["has_custom_generate"] = self._generate_fn is not None
        return base
