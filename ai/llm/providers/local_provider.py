from __future__ import annotations

from typing import Any, AsyncIterator

from .base_provider import BaseLLMProvider


class LocalProvider(BaseLLMProvider):
    """Local model provider (e.g. Ollama, llama.cpp)."""

    def __init__(self, model: str = "local-model", endpoint: str = "http://localhost:11434") -> None:
        super().__init__(name="local", model=model)
        self._endpoint = endpoint

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return {
            "content": f"Local ({self._model}) response to: {prompt[:50]}...",
            "success": True,
            "tokens_prompt": len(prompt) // 4,
            "tokens_completion": 64,
            "finish_reason": "stop",
            "cost_usd": 0.0,
        }

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _gen() -> AsyncIterator[dict[str, Any]]:
            yield {"content": f"Local ({self._model}) streaming...", "finish_reason": "stop"}
        return _gen()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["endpoint"] = self._endpoint
        return base
