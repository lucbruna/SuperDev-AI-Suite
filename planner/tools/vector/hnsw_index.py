from __future__ import annotations

from typing import Any


class HNSWIndex:
    """Hierarchical Navigable Small World index for approximate nearest neighbor search."""

    def __init__(self, dim: int = 1536, M: int = 16, ef_construction: int = 200):
        self.dim = dim
        self.M = M
        self.ef_construction = ef_construction
        self._vectors: dict[str, list[float]] = {}

    def add(self, id: str, vector: list[float]) -> None:
        self._vectors[id] = vector

    def search(self, query: list[float], top_k: int = 10) -> list[dict[str, Any]]:
        results = []
        for id, vector in self._vectors.items():
            score = self._cosine(query, vector)
            results.append({"id": id, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _cosine(self, a: list[float], b: list[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        return dot / (na * nb) if na and nb else 0.0
