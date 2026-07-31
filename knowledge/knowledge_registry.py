from __future__ import annotations

import logging
from typing import Any, Callable


class KnowledgeRegistry:
    """Registry of knowledge components: providers, processors, loaders, and rules."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.registry")
        self._embedding_providers: dict[str, Any] = {}
        self._vector_backends: dict[str, Any] = {}
        self._document_processors: dict[str, Any] = {}
        self._loaders: dict[str, Any] = {}
        self._chunkers: dict[str, Any] = {}
        self._rules: list[Any] = []
        self._factories: dict[str, Callable[..., Any]] = {}

    def register_embedding_provider(self, name: str, provider: Any) -> None:
        self._embedding_providers[name] = provider

    def get_embedding_provider(self, name: str) -> Any:
        return self._embedding_providers.get(name)

    def register_vector_backend(self, name: str, backend: Any) -> None:
        self._vector_backends[name] = backend

    def get_vector_backend(self, name: str) -> Any:
        return self._vector_backends.get(name)

    def register_document_processor(self, name: str, processor: Any) -> None:
        self._document_processors[name] = processor

    def get_document_processor(self, name: str) -> Any:
        return self._document_processors.get(name)

    def register_loader(self, name: str, loader: Any) -> None:
        self._loaders[name] = loader

    def get_loader(self, name: str) -> Any:
        return self._loaders.get(name)

    def register_chunker(self, name: str, chunker: Any) -> None:
        self._chunkers[name] = chunker

    def get_chunker(self, name: str) -> Any:
        return self._chunkers.get(name)

    def register_rule(self, rule: Any) -> None:
        self._rules.append(rule)

    def list_rules(self) -> list[Any]:
        return list(self._rules)

    def register_factory(self, name: str, factory: Callable[..., Any]) -> None:
        self._factories[name] = factory

    def get_factory(self, name: str) -> Callable[..., Any] | None:
        return self._factories.get(name)

    def snapshot(self) -> dict[str, int]:
        return {
            "embedding_providers": len(self._embedding_providers),
            "vector_backends": len(self._vector_backends),
            "document_processors": len(self._document_processors),
            "loaders": len(self._loaders),
            "chunkers": len(self._chunkers),
            "rules": len(self._rules),
            "factories": len(self._factories),
        }
