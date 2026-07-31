from __future__ import annotations

from typing import Any

from .embedding_repository import EmbeddingRepository
from .similarity_engine import SimilarityEngine


class VectorStore:
    """In-memory vector store with CRUD and similarity search."""

    def __init__(self, repository: EmbeddingRepository | None = None):
        self._vectors: dict[str, list[float]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._repository = repository or EmbeddingRepository()
        self._similarity = SimilarityEngine()
        self._dimension: int = 0

    @property
    def count(self) -> int:
        return len(self._vectors)

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def vector_ids(self) -> list[str]:
        return list(self._vectors.keys())

    def insert(self, vector_id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> None:
        if self._vectors and len(vector) != self._dimension:
            raise ValueError(f"Expected dimension {self._dimension}, got {len(vector)}")
        if not self._vectors:
            self._dimension = len(vector)
        self._vectors[vector_id] = list(vector)
        self._metadata[vector_id] = dict(metadata or {})
        self._repository.store(vector_id, vector, metadata or {})

    def get(self, vector_id: str) -> list[float] | None:
        return self._vectors.get(vector_id)

    def get_metadata(self, vector_id: str) -> dict[str, Any]:
        return dict(self._metadata.get(vector_id, {}))

    def update(self, vector_id: str, vector: list[float], metadata: dict[str, Any] | None = None) -> bool:
        if vector_id not in self._vectors:
            return False
        if len(vector) != self._dimension:
            raise ValueError(f"Expected dimension {self._dimension}, got {len(vector)}")
        self._vectors[vector_id] = list(vector)
        if metadata is not None:
            self._metadata[vector_id] = dict(metadata)
        self._repository.update(vector_id, vector, metadata or {})
        return True

    def delete(self, vector_id: str) -> bool:
        if vector_id not in self._vectors:
            return False
        del self._vectors[vector_id]
        self._metadata.pop(vector_id, None)
        self._repository.remove(vector_id)
        return True

    def similarity_search(
        self, query_vector: list[float], top_k: int = 10, metric: str = "cosine"
    ) -> list[tuple[str, float]]:
        if not self._vectors:
            return []
        scores: list[tuple[str, float]] = []
        for vid, vec in self._vectors.items():
            sim = self._similarity.compare(query_vector, vec, metric)
            scores.append((vid, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

    def batch_insert(self, items: list[tuple[str, list[float], dict[str, Any]]]) -> None:
        for vid, vec, meta in items:
            self.insert(vid, vec, meta)

    def clear(self) -> None:
        self._vectors.clear()
        self._metadata.clear()

    def exists(self, vector_id: str) -> bool:
        return vector_id in self._vectors
