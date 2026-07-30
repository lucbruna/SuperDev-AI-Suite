from __future__ import annotations

from typing import Any


class Retriever:
    """Document retriever using vector search."""

    def __init__(self):
        self._documents: dict[str, str] = {}
        self._vectors: dict[str, list[float]] = {}

    def index(self, doc_id: str, text: str, vector: list[float]) -> None:
        self._documents[doc_id] = text
        self._vectors[doc_id] = vector

    def retrieve(self, query_vector: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        results = []
        for doc_id, vector in self._vectors.items():
            score = self._cosine(query_vector, vector)
            results.append({"id": doc_id, "text": self._documents[doc_id], "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def _cosine(self, a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        return dot / (na * nb) if na and nb else 0.0
