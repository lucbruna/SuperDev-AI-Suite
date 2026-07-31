"""Local model provider."""

from __future__ import annotations

from typing import Any


class LocalProvider:
    def __init__(self, model_path: str = "", model_name: str = "local-model") -> None:
        self._model_path = model_path
        self._model_name = model_name
        self._loaded = False
        self._requests = 0

    def load(self) -> bool:
        self._loaded = True
        return True

    def unload(self) -> bool:
        self._loaded = False
        return True

    def complete(self, prompt: str, max_tokens: int = 1024, **kwargs: Any) -> dict[str, Any]:
        if not self._loaded:
            return {"error": "model_not_loaded", "status": "failed"}
        self._requests += 1
        tokens = len(prompt.split()) + max_tokens
        return {
            "content": f"[Local {self._model_name}] Response to: {prompt[:50]}...",
            "model": self._model_name,
            "tokens": tokens,
            "provider": "local",
            "status": "ok",
        }

    def is_loaded(self) -> bool:
        return self._loaded

    def get_models(self) -> list[str]:
        return [self._model_name]

    def get_stats(self) -> dict[str, Any]:
        return {"requests": self._requests, "loaded": self._loaded}

    def get_model_info(self) -> dict[str, Any]:
        return {"name": self._model_name, "path": self._model_path, "loaded": self._loaded}
