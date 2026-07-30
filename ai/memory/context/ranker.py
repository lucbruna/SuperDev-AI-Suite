from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


class ContextRanker:
    """Ranks context items by relevance, recency, importance, or custom criteria."""

    def __init__(self):
        self._ranking_count: int = 0

    @property
    def ranking_count(self) -> int:
        return self._ranking_count

    def rank_by_relevance(self, items: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for item in items:
            score = 0.0
            content = str(item.get("content", ""))
            score += content.lower().count(q) * 0.1
            name = str(item.get("source", item.get("name", "")))
            if q in name.lower():
                score += 1.0
            tags = item.get("metadata", {}).get("tags", [])
            if q in [str(t).lower() for t in tags]:
                score += 0.5
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        self._ranking_count += 1
        return [item for _, item in scored]

    def rank_by_recency(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def recency_key(item: Dict[str, Any]) -> float:
            return float(item.get("metadata", {}).get("timestamp", 0.0))

        result = sorted(items, key=recency_key, reverse=True)
        self._ranking_count += 1
        return result

    def rank_by_importance(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        def importance_key(item: Dict[str, Any]) -> float:
            return float(item.get("metadata", {}).get("importance", 0.0))

        result = sorted(items, key=importance_key, reverse=True)
        self._ranking_count += 1
        return result

    def rank_custom(
        self, items: List[Dict[str, Any]], key_fn: Any
    ) -> List[Dict[str, Any]]:
        result = sorted(items, key=key_fn, reverse=True)
        self._ranking_count += 1
        return result

    def top_k(self, items: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
        return items[:k]

    def reset(self) -> None:
        self._ranking_count = 0
