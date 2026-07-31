from __future__ import annotations

import logging
from typing import Any


class Ranking:
    """Ranks and reranks search results."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.vector_store.ranking")

    def sort_by_score(self, results: list[Any], descending: bool = True) -> list[Any]:
        return sorted(results, key=lambda r: r.score, reverse=descending)

    def weighted(self, results: list[Any], relevance_weight: float = 1.0,
                 recency_weight: float = 0.0) -> list[Any]:
        for result in results:
            combined = result.score * relevance_weight
            if recency_weight and "created_at" in result.metadata:
                combined += recency_weight * 0.01  # recency boost placeholder
            result.metadata["ranked_score"] = combined
        return sorted(results, key=lambda r: r.metadata.get("ranked_score", r.score), reverse=True)

    def deduplicate(self, results: list[Any]) -> list[Any]:
        seen: set[str] = set()
        unique: list[Any] = []
        for result in results:
            key = result.text.strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(result)
        return unique

    def top_k(self, results: list[Any], k: int) -> list[Any]:
        return results[:k]
