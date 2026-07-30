from __future__ import annotations

from typing import Any


class PQIndex:
    """Product Quantization index for compressed vector search."""

    def __init__(self, m: int = 8, k: int = 256):
        self.m = m
        self.k = k
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
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        return dot / (na * nb) if na and nb else 0.0
