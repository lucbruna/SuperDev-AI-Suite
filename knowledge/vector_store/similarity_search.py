from __future__ import annotations

import logging
from typing import Any

from ..embeddings.similarity import Similarity
from ..knowledge_models import Embedding, SearchResult


class SimilaritySearch:
    """Performs vector similarity queries against a set of embeddings."""

    def __init__(self, method: str = "cosine") -> None:
        self._log = logging.getLogger("superdev.knowledge.vector_store.similarity_search")
        self._method = method

    def search(self, query_vector: list[float], embeddings: list[Embedding],
               top_k: int = 5, threshold: float = 0.0) -> list[SearchResult]:
        scored = []
        for embedding in embeddings:
            score = self._score(query_vector, embedding.vector)
            if score >= threshold:
                scored.append((score, embedding))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            SearchResult(
                text=e.text, score=score, document_id=e.document_id,
                source=e.metadata.get("source", "vector"), metadata=dict(e.metadata),
            )
            for score, e in scored[:top_k]
        ]

    def _score(self, left: list[float], right: list[float]) -> float:
        if self._method == "dot":
            return Similarity.dot_product(left, right)
        if self._method == "euclidean":
            distance = Similarity.euclidean(left, right)
            return 1.0 / (1.0 + distance)
        return Similarity.cosine(left, right)
