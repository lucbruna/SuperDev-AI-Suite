from __future__ import annotations

from typing import Any


class EmbeddingRegistry:
    """Registry for embedding models."""

    def __init__(self):
        self._models: dict[str, Any] = {}

    def register(self, name: str, model: Any) -> None:
        self._models[name] = model

    def get(self, name: str) -> Any | None:
        return self._models.get(name)

    def list_models(self) -> list[str]:
        return list(self._models.keys())

    def unregister(self, name: str) -> None:
        self._models.pop(name, None)
