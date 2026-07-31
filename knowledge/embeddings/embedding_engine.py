from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_interfaces import Chunker, EmbeddingProvider
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import Chunk, Embedding
from .chunking import SlidingWindowChunker
from .metadata import EmbeddingMetadata
from .model_manager import ModelManager


class EmbeddingEngine:
    """Produces embeddings and chunks for downstream indexing."""

    def __init__(
        self,
        config: KnowledgeConfig | None = None,
        model_manager: ModelManager | None = None,
        chunker: Chunker | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.model_manager = model_manager or ModelManager(
            self.config.embedding_model, self.config.embedding_dimensions
        )
        self.chunker = chunker or SlidingWindowChunker(
            self.config.chunk_size, self.config.chunk_overlap
        )
        self.metadata_builder = EmbeddingMetadata()

    def embed(self, text: str, model: str | None = None) -> list[float]:
        provider = self.model_manager.get(model)
        with self.metrics.time("embeddings.engine.embed"):
            vector = provider.embed(text)
        self.metrics.increment("embeddings.engine.vectors")
        return vector

    def embed_chunks(self, chunks: list[Chunk]) -> list[Embedding]:
        embeddings: list[Embedding] = []
        for chunk in chunks:
            vector = self.embed(chunk.text)
            embeddings.append(
                Embedding(
                    vector=vector,
                    text=chunk.text,
                    document_id=chunk.document_id,
                    metadata={**chunk.metadata, "chunk_index": chunk.index},
                )
            )
        self.events.emit(KnowledgeEventType.EMBEDDING_CREATED, {"count": len(embeddings)})
        return embeddings

    def split_and_embed(self, text: str, document_id: str = "") -> list[Embedding]:
        chunks = self.chunker.chunk(text, document_id)
        return self.embed_chunks(chunks)

    def chunk_text(self, text: str, document_id: str = "") -> list[Chunk]:
        return self.chunker.chunk(text, document_id)

    def status(self) -> dict[str, Any]:
        return {
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap,
            "models": self.model_manager.status(),
        }
