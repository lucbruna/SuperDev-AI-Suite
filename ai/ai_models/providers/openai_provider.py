"""OpenAI provider."""
from __future__ import annotations

from typing import Any


class OpenAIProvider:
    def __init__(self, api_key: str = "", model: str = "gpt-4") -> None:
        self._api_key = api_key
        self._model = model
        self._requests = 0
        self._total_tokens = 0
    def complete(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7, **kwargs: Any) -> dict[str, Any]:
        self._requests += 1
        tokens = len(prompt.split()) + max_tokens
        self._total_tokens += tokens
        return {"content": f"[OpenAI {self._model}] Response to: {prompt[:50]}...", "model": self._model, "tokens": tokens, "provider": "openai", "status": "ok"}
    def stream(self, prompt: str, **kwargs: Any):
        yield {"chunk": f"Streaming from {self._model}..."}
    def get_models(self) -> list[str]:
        return ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "o1", "o1-mini"]
    def get_stats(self) -> dict[str, int]:
        return {"requests": self._requests, "total_tokens": self._total_tokens}
    def set_model(self, model: str) -> None:
        self._model = model
    def get_model(self) -> str:
        return self._model
