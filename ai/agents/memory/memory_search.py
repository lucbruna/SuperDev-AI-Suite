"""Cross-memory search engine."""
from __future__ import annotations

from typing import Any


class MemorySearch:
    """Unified search across all memory backends with relevance scoring."""

    def __init__(self) -> None:
        self._search_count: int = 0

    def search(self, memory: Any, query: str,
               limit: int = 10) -> list[dict[str, Any]]:
        self._search_count += 1
        results: list[dict[str, Any]] = []
        query_lower = query.lower()
        if hasattr(memory, "get_all"):
            all_items = memory.get_all()
            for key, value in all_items.items():
                score = self._score_match(query_lower, key, value)
                if score > 0:
                    results.append({
                        "key": key,
                        "value": value,
                        "score": round(score, 4),
                    })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def search_multiple(self, memories: list[Any], query: str,
                        limit: int = 10) -> list[dict[str, Any]]:
        combined: list[dict[str, Any]] = []
        for mem in memories:
            combined.extend(self.search(mem, query, limit * 2))
        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined[:limit]

    def _score_match(self, query: str, key: str, value: Any) -> float:
        score = 0.0
        key_lower = key.lower()
        if query in key_lower:
            score += 0.8
        elif any(w in key_lower for w in query.split()):
            score += 0.4
        text = str(value).lower()
        if query in text:
            score += 0.6
        elif any(w in text for w in query.split()):
            score += 0.2
        return min(score, 1.0)

    def snapshot(self) -> dict[str, Any]:
        return {"total_searches": self._search_count}
