from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import Embedding, SearchResult
from .filtering import Filtering
from .similarity_search import SimilaritySearch


class CollectionManager:
    """Manages multiple named vector collections."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.vector_store.collection_manager")
        self._collections: dict[str, list[Embedding]] = {}
        self._searcher = SimilaritySearch()
        self._filtering = Filtering()

    def create(self, name: str) -> bool:
        if name in self._collections:
            return False
        self._collections[name] = []
        return True

    def delete(self, name: str) -> bool:
        return self._collections.pop(name, None) is not None

    def add(self, name: str, embedding: Embedding) -> str:
        if name not in self._collections:
            self.create(name)
        self._collections[name].append(embedding)
        return f"{name}:{len(self._collections[name]) - 1}"

    def search(self, name: str, query_vector: list[float], top_k: int = 5,
               threshold: float = 0.0, metadata_eq: dict[str, Any] | None = None) -> list[SearchResult]:
        embeddings = self._collections.get(name, [])
        results = self._searcher.search(query_vector, embeddings, top_k, threshold)
        return self._filtering.apply(results, metadata_eq=metadata_eq)

    def list(self) -> list[str]:
        return sorted(self._collections)

    def count(self, name: str) -> int:
        return len(self._collections.get(name, []))
