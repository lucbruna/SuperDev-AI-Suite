from __future__ import annotations

import logging
from typing import Any

from .knowledge_config import KnowledgeConfig
from .knowledge_events import KnowledgeEvents, KnowledgeEventType
from .knowledge_interfaces import (
    DocumentStore,
    EmbeddingProvider,
    MemoryStore,
    VectorStore,
)
from .knowledge_metrics import KnowledgeMetrics
from .knowledge_models import (
    DocumentRecord,
    Embedding,
    KnowledgeItem,
    MemoryRecord,
    SearchResult,
)
from .knowledge_registry import KnowledgeRegistry
from .knowledge_security import KnowledgeSecurity


class KnowledgeManager:
    """High-level orchestration of memory, documents, embeddings, and search."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        memory_store: MemoryStore | None = None,
        document_store: DocumentStore | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
        registry: KnowledgeRegistry | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
        security: KnowledgeSecurity | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.manager")
        self.config = config or KnowledgeConfig()
        self.registry = registry or KnowledgeRegistry()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.security = security or KnowledgeSecurity(self.config.enable_governance)
        self.memory_store = memory_store
        self.document_store = document_store
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    # --- Memory -----------------------------------------------------------

    def store_memory(self, content: str, memory_type: str = "episodic", importance: float = 0.5,
                     metadata: dict[str, Any] | None = None) -> str:
        if not self.memory_store:
            raise RuntimeError("memory store is not configured")
        record = MemoryRecord(
            content=content, memory_type=memory_type, importance=importance,
            metadata=metadata or {},
        )
        record_id = self.memory_store.save(record)
        self.metrics.increment("memory.stored")
        self.events.emit(KnowledgeEventType.MEMORY_STORED, {"record_id": record_id})
        return record_id

    def recall_memory(self, memory_type: str | None = None) -> list[MemoryRecord]:
        if not self.memory_store:
            return []
        records = self.memory_store.list(memory_type)
        self.metrics.increment("memory.recalled")
        self.events.emit(KnowledgeEventType.MEMORY_RECALLED, {"count": len(records)})
        return records

    def delete_memory(self, record_id: str) -> bool:
        if not self.memory_store:
            return False
        return self.memory_store.delete(record_id)

    # --- Documents --------------------------------------------------------

    def add_document(self, document: DocumentRecord) -> str:
        if not self.document_store:
            raise RuntimeError("document store is not configured")
        document_id = self.document_store.add(document)
        self.metrics.increment("documents.added")
        self.events.emit(KnowledgeEventType.DOCUMENT_ADDED, {"document_id": document_id})
        return document_id

    def get_document(self, document_id: str) -> DocumentRecord | None:
        if not self.document_store:
            return None
        return self.document_store.get(document_id)

    def update_document(self, document_id: str, document: DocumentRecord) -> bool:
        if not self.document_store:
            return False
        document.version += 1
        updated = self.document_store.update(document_id, document)
        if updated:
            self.events.emit(KnowledgeEventType.DOCUMENT_UPDATED, {"document_id": document_id})
        return updated

    def list_documents(self) -> list[DocumentRecord]:
        if not self.document_store:
            return []
        return self.document_store.list()

    # --- Embeddings & vectors ----------------------------------------------

    def embed(self, text: str) -> list[float]:
        if not self.embedding_provider:
            raise RuntimeError("embedding provider is not configured")
        with self.metrics.time("embedding.embed"):
            vector = self.embedding_provider.embed(text)
        self.metrics.increment("embeddings.created")
        self.events.emit(KnowledgeEventType.EMBEDDING_CREATED, {"dimensions": len(vector)})
        return vector

    def index_embedding(self, text: str, document_id: str = "",
                        metadata: dict[str, Any] | None = None) -> str:
        if not self.vector_store:
            raise RuntimeError("vector store is not configured")
        vector = self.embed(text)
        embedding = Embedding(
            vector=vector, text=text, document_id=document_id, metadata=metadata or {},
        )
        return self.vector_store.add(embedding)

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if not self.vector_store:
            return []
        query_vector = self.embed(query)
        with self.metrics.time("search.vector"):
            results = self.vector_store.search(query_vector, top_k=top_k)
        self.metrics.increment("search.executed")
        self.events.emit(KnowledgeEventType.SEARCH_EXECUTED, {"hits": len(results)})
        return results

    # --- Lifecycle ----------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "workspace_id": self.config.workspace_id,
            "memory_configured": self.memory_store is not None,
            "documents_configured": self.document_store is not None,
            "embeddings_configured": self.embedding_provider is not None,
            "vectors_configured": self.vector_store is not None,
            "metrics": self.metrics.snapshot(),
            "registry": self.registry.snapshot(),
        }

    def store(self, item: KnowledgeItem) -> str:
        return self.store_memory(item.content, memory_type=item.kind, metadata=item.metadata)
