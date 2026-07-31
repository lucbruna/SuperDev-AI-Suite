"""Vector indexing: chunking texts and embedding them for retrieval."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.vector.embedding_manager import EmbeddingManager


class VectorIndexing:
    """Builds embeddable chunks from documents/text."""

    def __init__(self, embeddings: EmbeddingManager | None = None,
                 chunk_size: int = 256) -> None:
        self.embeddings = embeddings or EmbeddingManager()
        self.chunk_size = max(1, int(chunk_size))

    def chunk(self, text: str) -> list[str]:
        words = (text or "").split()
        return [" ".join(words[i:i + self.chunk_size])
                for i in range(0, len(words), self.chunk_size)]

    def embed_chunk(self, chunk: str, chunk_id: str,
                    metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        vector = self.embeddings.embed(chunk)
        return {"chunk_id": chunk_id, "text": chunk, "vector": vector,
                "metadata": dict(metadata or {})}

    def index_text(self, text: str, prefix: str = "chunk",
                   metadata: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        chunks = self.chunk(text)
        return [self.embed_chunk(chunk, f"{prefix}-{index}",
                                 metadata or {})
                for index, chunk in enumerate(chunks)]

    def stats(self) -> dict[str, Any]:
        return self.embeddings.stats()
