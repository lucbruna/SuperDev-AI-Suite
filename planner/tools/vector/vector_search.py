from __future__ import annotations

from typing import Any


class VectorSearch:
    """Search implementation for vector similarity."""

    def __init__(self):
        self._vectors: dict[str, list[float]] = {}

    def add(self, id: str, vector: list[float]) -> None:
        self._vectors[id] = vector

    def search(self, query: list[float], top_k: int = 10) -> list[dict[str, Any]]:
        results = []
        for id, vector in self._vectors.items():
            score = self._cosine_similarity(query, vector)
            results.append({"id": id, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
