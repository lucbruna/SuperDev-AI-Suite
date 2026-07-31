"""Similarity functions for vector memory."""

from __future__ import annotations

import math
from typing import Any


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity in [0, 1] (embeddings are non-negative signed)."""
    if len(a) != len(b) or not a:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))


def dot(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def euclidean(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return float("inf")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class SimilaritySearch:
    """Ranks vectors by similarity against a query vector."""

    def __init__(self, metric: str = "cosine") -> None:
        self.metric = metric

    def _score(self, a: list[float], b: list[float]) -> float:
        if self.metric == "euclidean":
            return 1.0 / (1.0 + euclidean(a, b))
        return cosine(a, b)

    def rank(self, query: list[float],
             candidates: list[dict[str, Any]],
             limit: int = 10) -> list[dict[str, Any]]:
        """``candidates`` are dicts with a ``vector`` key."""
        scored = []
        for candidate in candidates:
            score = self._score(query, candidate.get("vector", []))
            if score <= 0:
                continue
            item = dict(candidate)
            item["score"] = score
            scored.append(item)
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:max(0, limit)]
