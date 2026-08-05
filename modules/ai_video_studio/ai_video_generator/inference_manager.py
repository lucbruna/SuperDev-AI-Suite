"""Inference manager — abstract model inference lifecycle."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import AIError


class InferenceManager:
    """Loads, caches and runs inference through registered providers."""

    def __init__(self) -> None:
        self._providers: dict[str, Any] = {}
        self._loaded: dict[str, bool] = {}

    def register_provider(self, name: str, provider: Any) -> None:
        self._providers[name] = provider

    def load(self, model: str, *, provider: str = "default") -> bool:
        prov = self._providers.get(provider)
        if prov is None:
            raise AIError(f"Unknown provider '{provider}'")
        self._loaded[model] = True
        return True

    def is_loaded(self, model: str) -> bool:
        return self._loaded.get(model, False)

    def predict(self, model: str, inputs: dict[str, Any]) -> dict[str, Any]:
        if not self.is_loaded(model):
            raise AIError(f"Model '{model}' is not loaded")
        provider = next((p for p in self._providers.values() if hasattr(p, "predict")), None)
        if provider is None:
            # Deterministic no-op prediction for offline/dev usage.
            return {"output": inputs, "provider": "fallback"}
        return provider.predict(model, inputs)

    def unload(self, model: str) -> None:
        self._loaded.pop(model, None)


_inference_manager: InferenceManager | None = None


def get_inference_manager() -> InferenceManager:
    global _inference_manager
    if _inference_manager is None:
        _inference_manager = InferenceManager()
    return _inference_manager
