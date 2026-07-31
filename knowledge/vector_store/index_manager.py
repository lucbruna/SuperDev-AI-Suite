from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import Embedding, SearchResult
from .similarity_search import SimilaritySearch


class IndexManager:
    """Tracks and searches a collection of indexed embeddings."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.vector_store.index_manager")
        self._embeddings: list[Embedding] = []
        self._ids: dict[str, int] = {}
        self._searcher = SimilaritySearch()

    def add(self, embedding: Embedding) -> str:
        index = len(self._embeddings)
        self._embeddings.append(embedding)
        embedding_id = f"idx-{index}"
        self._ids[embedding_id] = index
        return embedding_id

    def search(self, query_vector: list[float], top_k: int = 5, threshold: float = 0.0) -> list[SearchResult]:
        return self._searcher.search(query_vector, self._embeddings, top_k, threshold)

    def delete(self, embedding_id: str) -> bool:
        index = self._ids.pop(embedding_id, None)
        if index is None:
            return False
        self._embeddings[index] = Embedding(vector=[], text="__deleted__")
        return True

    def count(self) -> int:
        return len([e for e in self._embeddings if e.text != "__deleted__"])

    def size(self) -> int:
        return len(self._embeddings)

    def all(self) -> list[Embedding]:
        return list(self._embeddings)

    def status(self) -> dict[str, Any]:
        return {"indexed": self.count(), "capacity": self.size()}
