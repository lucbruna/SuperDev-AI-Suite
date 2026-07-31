"""Ollama provider."""
from __future__ import annotations

from typing import Any


class OllamaProvider:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2") -> None:
        self._base_url = base_url
        self._model = model
        self._requests = 0
    def complete(self, prompt: str, max_tokens: int = 1024, **kwargs: Any) -> dict[str, Any]:
        self._requests += 1
        tokens = len(prompt.split()) + max_tokens
        return {"content": f"[Ollama {self._model}] Response to: {prompt[:50]}...", "model": self._model, "tokens": tokens, "provider": "ollama", "status": "ok"}
    def list_local_models(self) -> list[str]:
        return ["llama2", "codellama", "mistral", "vicuna"]
    def pull_model(self, model_name: str) -> dict[str, Any]:
        return {"model": model_name, "status": "pulling", "provider": "ollama"}
    def get_stats(self) -> dict[str, int]:
        return {"requests": self._requests}
    def set_model(self, model: str) -> None:
        self._model = model
    def is_available(self) -> bool:
        return True
