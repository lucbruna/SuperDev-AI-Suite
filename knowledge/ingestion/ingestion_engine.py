from __future__ import annotations

import logging
from typing import Any

from ..embeddings.chunking import SlidingWindowChunker
from ..embeddings.generator import HashEmbeddingGenerator
from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_interfaces import DocumentStore, VectorStore
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import DocumentRecord
from ..documents.document_manager import InMemoryDocumentManager
from ..vector_store.storage import InMemoryVectorStorage
from .pipeline import IngestionPipeline
from .tracker import IngestionTracker


class IngestionEngine:
    """Orchestrates the ingestion of documents into chunks and embeddings."""

    def __init__(
        self,
        document_store: DocumentStore | None = None,
        vector_store: VectorStore | None = None,
        chunker: Any | None = None,
        embedding_provider: Any | None = None,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.ingestion.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.document_store = document_store or InMemoryDocumentManager()
        self.vector_store = vector_store or InMemoryVectorStorage(self.config.similarity_threshold)
        self.pipeline = IngestionPipeline(
            chunker=chunker or SlidingWindowChunker(self.config.chunk_size, self.config.chunk_overlap),
            embedding_provider=embedding_provider or HashEmbeddingGenerator(self.config.embedding_dimensions),
            config=self.config,
        )
        self.tracker = IngestionTracker()

    def ingest_document(self, document: DocumentRecord) -> dict[str, Any]:
        document_id = self.document_store.add(document)
        staged = self.pipeline.run(document)
        staged["document_id"] = document_id
        for chunk in staged["chunks"]:
            chunk.document_id = document_id
        embedding_ids: list[str] = []
        for embedding in staged["embeddings"]:
            embedding.document_id = document_id
            embedding_ids.append(self.vector_store.add(embedding))
        self.metrics.increment("ingestion.documents")
        self.metrics.increment("ingestion.chunks", len(staged["chunks"]))
        self.events.emit(KnowledgeEventType.DOCUMENT_ADDED, {"document_id": document_id})
        self.tracker.record(document_id, "done", {"chunks": len(staged["chunks"])})
        return {
            "document_id": document_id,
            "chunks": len(staged["chunks"]),
            "embeddings": len(embedding_ids),
        }

    def ingest_batch(self, documents: list[DocumentRecord]) -> dict[str, Any]:
        from .batch_processor import BatchProcessor

        batch = BatchProcessor()
        summary = batch.process(documents, self.ingest_document)
        self._log.info("ingested batch: %s", summary)
        return summary

    def stats(self) -> dict[str, Any]:
        return {
            "documents": len(self.document_store.list()),
            "vectors": self.vector_store.count(),
            "tracker": self.tracker.stats(),
        }
