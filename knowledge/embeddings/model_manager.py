from __future__ import annotations

import logging
from typing import Any

from ..knowledge_interfaces import EmbeddingProvider
from .generator import HashEmbeddingGenerator


class ModelManager:
    """Selects and caches embedding model providers."""

    def __init__(self, default_model: str = "local-hash", dimensions: int = 384) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.model_manager")
        self._default_model = default_model
        self._providers: dict[str, EmbeddingProvider] = {}
        self._dimensions = dimensions
        self._register_builtin()

    def _register_builtin(self) -> None:
        self._providers["local-hash"] = HashEmbeddingGenerator(self._dimensions)

    def register(self, name: str, provider: EmbeddingProvider) -> None:
        self._providers[name] = provider

    def get(self, name: str | None = None) -> EmbeddingProvider:
        model = name or self._default_model
        provider = self._providers.get(model)
        if provider is None:
            raise KeyError(f"unknown embedding model: {model}")
        return provider

    def models(self) -> list[str]:
        return sorted(self._providers)

    def status(self) -> dict[str, Any]:
        return {
            "default": self._default_model,
            "models": self.models(),
            "dimensions": self._dimensions,
        }
