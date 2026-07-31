from __future__ import annotations

import logging
from typing import Any

from .knowledge_config import KnowledgeConfig
from .knowledge_manager import KnowledgeManager
from .knowledge_registry import KnowledgeRegistry


class KnowledgeFactory:
    """Builds knowledge components from configuration and registry providers."""

    def __init__(self, config: KnowledgeConfig | None = None, registry: KnowledgeRegistry | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.factory")
        self.config = config or KnowledgeConfig()
        self.registry = registry or KnowledgeRegistry()

    def build_memory_store(self) -> Any:
        backend = self.config.extra.get("memory_backend", "in-memory")
        factory = self.registry.get_factory(f"memory_store:{backend}")
        if factory is None:
            from .memory.memory_storage import InMemoryMemoryStorage

            return InMemoryMemoryStorage()
        return factory(self.config)

    def build_document_store(self) -> Any:
        factory = self.registry.get_factory("document_store")
        if factory is None:
            from .documents.document_manager import InMemoryDocumentManager

            return InMemoryDocumentManager()
        return factory(self.config)

    def build_embedding_provider(self) -> Any:
        backend = self.config.embedding_model
        provider = self.registry.get_embedding_provider(backend)
        if provider is None:
            from .embeddings.generator import HashEmbeddingGenerator

            return HashEmbeddingGenerator(self.config.embedding_dimensions)
        return provider

    def build_vector_store(self) -> Any:
        backend = self.config.vector_store_backend
        store = self.registry.get_vector_backend(backend)
        if store is None:
            from .vector_store.storage import InMemoryVectorStorage

            return InMemoryVectorStorage()
        return store

    def build_chunker(self) -> Any:
        chunker = self.registry.get_chunker(self.config.extra.get("chunker", "default"))
        if chunker is None:
            from .embeddings.chunking import SlidingWindowChunker

            return SlidingWindowChunker(self.config.chunk_size, self.config.chunk_overlap)
        return chunker

    def build_manager(self) -> KnowledgeManager:
        return KnowledgeManager(
            config=self.config,
            registry=self.registry,
            memory_store=self.build_memory_store(),
            document_store=self.build_document_store(),
            embedding_provider=self.build_embedding_provider(),
            vector_store=self.build_vector_store(),
        )
