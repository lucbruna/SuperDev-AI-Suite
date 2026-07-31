"""HuggingFace provider."""
from __future__ import annotations

from typing import Any


class HuggingFaceProvider:
    def __init__(self, api_key: str = "", model: str = "meta-llama/Llama-2-7b-chat-hf") -> None:
        self._api_key = api_key
        self._model = model
        self._requests = 0
    def complete(self, prompt: str, max_tokens: int = 1024, **kwargs: Any) -> dict[str, Any]:
        self._requests += 1
        tokens = len(prompt.split()) + max_tokens
        return {"content": f"[HuggingFace {self._model}] Response to: {prompt[:50]}...", "model": self._model, "tokens": tokens, "provider": "huggingface", "status": "ok"}
    def get_models(self) -> list[str]:
        return ["meta-llama/Llama-2-7b-chat-hf", "meta-llama/Llama-2-13b-chat-hf", "mistralai/Mistral-7B-v0.1"]
    def get_stats(self) -> dict[str, int]:
        return {"requests": self._requests}
    def set_model(self, model: str) -> None:
        self._model = model
