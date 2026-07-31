from __future__ import annotations

from typing import Any


class Relevance:
    """Computes relevance scores for retrieval results."""

    def __init__(self):
        self._relevance_count: int = 0

    @property
    def relevance_count(self) -> int:
        return self._relevance_count

    def compute(self, query: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q_words = set(query.lower().split())
        results: list[dict[str, Any]] = []
        for item in items:
            content = str(item.get("content", "")).lower()
            entry_words = set(content.split())
            overlap = len(q_words & entry_words)
            relevance = overlap / max(len(q_words | entry_words), 1)
            item["relevance"] = relevance
            results.append(item)
        self._relevance_count += 1
        return results

    def binary(self, query: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q = query.lower()
        for item in items:
            content = str(item.get("content", "")).lower()
            item["relevance"] = 1.0 if q in content else 0.0
        self._relevance_count += 1
        return items

    def threshold(self, items: list[dict[str, Any]], min_relevance: float = 0.5) -> list[dict[str, Any]]:
        return [item for item in items if item.get("relevance", 0) >= min_relevance]

    def feedback_adjust(self, items: list[dict[str, Any]], relevant_ids: list[str], boost: float = 0.2) -> list[dict[str, Any]]:
        for item in items:
            if item.get("id") in relevant_ids:
                item["relevance"] = item.get("relevance", 0) + boost
        self._relevance_count += 1
        return items

    def reset(self) -> None:
        self._relevance_count = 0
