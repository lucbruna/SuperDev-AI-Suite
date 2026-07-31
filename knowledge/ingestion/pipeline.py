from __future__ import annotations

import logging
from typing import Any

from ..embeddings.chunking import SlidingWindowChunker
from ..embeddings.generator import HashEmbeddingGenerator
from ..knowledge_config import KnowledgeConfig
from ..knowledge_models import Chunk, DocumentRecord, Embedding


class IngestionPipeline:
    """Runs the staged ingestion pipeline: preprocess -> chunk -> embed."""

    STAGES = ["preprocess", "chunk", "embed"]

    def __init__(
        self,
        chunker: Any | None = None,
        embedding_provider: Any | None = None,
        config: KnowledgeConfig | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.ingestion.pipeline")
        self.config = config or KnowledgeConfig()
        self.chunker = chunker or SlidingWindowChunker(self.config.chunk_size, self.config.chunk_overlap)
        self.embedding_provider = embedding_provider or HashEmbeddingGenerator(self.config.embedding_dimensions)

    def preprocess(self, text: str) -> str:
        from .preprocessor import Preprocessor

        return Preprocessor().clean(text)

    def chunk(self, text: str, document_id: str = "") -> list[Chunk]:
        return self.chunker.chunk(text, document_id)

    def embed(self, chunk: Chunk) -> Embedding:
        vector = self.embedding_provider.embed(chunk.text)
        return Embedding(
            vector=vector, text=chunk.text, document_id=chunk.document_id,
            metadata=dict(chunk.metadata),
        )

    def run(self, document: DocumentRecord) -> dict[str, Any]:
        cleaned = self.preprocess(document.content)
        chunks = self.chunk(cleaned)
        embeddings = [self.embed(chunk) for chunk in chunks]
        result = {
            "document_id": "",
            "chunks": chunks,
            "embeddings": embeddings,
        }
        self._log.debug("pipeline produced %d chunks and %d embeddings", len(chunks), len(embeddings))
        return result
