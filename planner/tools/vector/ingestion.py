from __future__ import annotations

from typing import Any

from .chunking import Chunking
from .embedding_engine import EmbeddingEngine
from .vector_store import VectorStore


class IngestionPipeline:
    """End-to-end document ingestion pipeline."""

    def __init__(
        self,
        chunker: Chunking | None = None,
        embedder: EmbeddingEngine | None = None,
        store: VectorStore | None = None,
    ):
        self.chunker = chunker or Chunking()
        self.embedder = embedder or EmbeddingEngine()
        self.store = store or VectorStore()

    def process_document(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> int:
        chunks = self.chunker.fixed_size(text)
        chunks = self.chunk(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}:chunk:{i}"
            self.store.add(chunk_id, [0.0], {"text": chunk, "doc_id": doc_id, **(metadata or {})})
        return len(chunks)

    def chunk(self, text: str) -> list[str]:
        return self.chunker.fixed_size(text)

    def index(
        self,
        doc_id: str,
        chunks: list[str],
        vectors: list[list[float]],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            self.store.add(f"{doc_id}:chunk:{i}", vector, {"text": chunk, "doc_id": doc_id, **(metadata or {})})
