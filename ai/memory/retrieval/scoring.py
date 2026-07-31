from __future__ import annotations

from typing import Any


class Scoring:
    """Scores retrieval results against a query."""

    def __init__(self):
        self._scoring_count: int = 0

    @property
    def scoring_count(self) -> int:
        return self._scoring_count

    def score(self, query: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q_words = set(query.lower().split())
        scored: list[dict[str, Any]] = []
        for item in items:
            content = str(item.get("content", "")).lower()
            entry_words = set(content.split())
            overlap = len(q_words & entry_words)
            score = overlap / max(len(q_words | entry_words), 1)
            scored.append({**item, "score": score})
        self._scoring_count += 1
        return scored

    def score_boolean(self, query: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q = query.lower()
        scored: list[dict[str, Any]] = []
        for item in items:
            content = str(item.get("content", "")).lower()
            score = 1.0 if q in content else 0.0
            scored.append({**item, "score": score})
        self._scoring_count += 1
        return scored

    def score_weighted(
        self, query: str, items: list[dict[str, Any]], weights: dict[str, float]
    ) -> list[dict[str, Any]]:
        q_words = set(query.lower().split())
        scored: list[dict[str, Any]] = []
        for item in items:
            total = 0.0
            for field, weight in weights.items():
                val = str(item.get(field, "")).lower()
                field_words = set(val.split())
                overlap = len(q_words & field_words)
                total += weight * (overlap / max(len(q_words | field_words), 1))
            scored.append({**item, "score": total})
        self._scoring_count += 1
        return scored

    def reset(self) -> None:
        self._scoring_count = 0
