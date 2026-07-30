from __future__ import annotations

from typing import Any, AsyncIterator

from ..llm_interfaces import ILLMProvider


class BaseLLMProvider(ILLMProvider):
    """Base class for all LLM provider implementations."""

    def __init__(self, name: str = "", model: str = "") -> None:
        self._name = name
        self._model = model

    def name(self) -> str:
        return self._name

    def model(self) -> str:
        return self._model

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _empty_gen() -> AsyncIterator[dict[str, Any]]:
            yield {"content": "", "finish_reason": "stop"}
        return _empty_gen()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    async def rollback(self) -> None:
        self._model = getattr(self, "_original_model", self._model)

    async def cleanup(self) -> None:
        pass

    def _ensure_deterministic(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        kwargs["temperature"] = 0.0
        kwargs["top_p"] = 1.0
        return kwargs

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "model": self._model,
        }
