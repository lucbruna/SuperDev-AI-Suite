"""Model registry — catalogue of generation models with capabilities."""
from __future__ import annotations

from typing import Any


class ModelRegistry:
    """Registry of known models and their metadata."""

    def __init__(self) -> None:
        self._models: dict[str, dict[str, Any]] = {
            "wan": {
                "type": "diffusion",
                "modes": ["text_to_video"],
                "gpu_mb": 8000,
                "quantizations": ["fp16", "int8"],
            },
            "image_to_video": {
                "type": "diffusion",
                "modes": ["image_to_video"],
                "gpu_mb": 8000,
                "quantizations": ["fp16"],
            },
            "video_to_video": {
                "type": "diffusion",
                "modes": ["video_to_video"],
                "gpu_mb": 6000,
                "quantizations": ["fp16", "int8"],
            },
        }

    def register(self, name: str, metadata: dict[str, Any]) -> None:
        self._models[name] = metadata

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._models[name]) if name in self._models else None

    def supports(self, name: str, mode: str) -> bool:
        meta = self._models.get(name)
        return bool(meta and mode in meta.get("modes", []))

    def list(self) -> list[str]:
        return list(self._models.keys())

    def by_mode(self, mode: str) -> list[str]:
        return [name for name, meta in self._models.items() if mode in meta.get("modes", [])]


_model_registry: ModelRegistry | None = None


def get_model_registry() -> ModelRegistry:
    global _model_registry
    if _model_registry is None:
        _model_registry = ModelRegistry()
    return _model_registry
