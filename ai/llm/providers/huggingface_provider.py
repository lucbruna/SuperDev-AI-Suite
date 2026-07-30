from __future__ import annotations

from typing import Any, AsyncIterator

from .base_provider import BaseLLMProvider


class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace Inference provider."""

    def __init__(self, model: str = "mistral-7b", api_token: str = "") -> None:
        super().__init__(name="huggingface", model=model)
        self._api_token = api_token

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return {
            "content": f"HuggingFace ({self._model}) response to: {prompt[:50]}...",
            "success": True,
            "tokens_prompt": len(prompt) // 4,
            "tokens_completion": 96,
            "finish_reason": "stop",
            "cost_usd": 0.0001,
        }

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _gen() -> AsyncIterator[dict[str, Any]]:
            yield {"content": f"HF ({self._model}) streaming...", "finish_reason": "stop"}
        return _gen()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["api_token_set"] = bool(self._api_token)
        return base
