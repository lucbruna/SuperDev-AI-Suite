"""Vector-based memory for semantic similarity search."""
from __future__ import annotations

import math
import time
from typing import Any


def _simple_hash_embedding(text: str, dim: int = 128) -> list[float]:
    """Deterministic pseudo-embedding from text via hash-based features."""
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(text[:200]))
    embedding = []
    for i in range(dim):
        val = math.sin(seed * (i + 1) * 0.1) * 0.5 + math.cos(seed * (i + 1) * 0.07) * 0.5
        embedding.append(round(val, 6))
    norm = math.sqrt(sum(v * v for v in embedding)) or 1.0
    return [v / norm for v in embedding]


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(x * x for x in b)) or 1.0
    return dot / (na * nb)


class VectorMemory:
    """Vector-based memory for semantic similarity search."""

    def __init__(self, embedding_dim: int = 128) -> None:
        self._embedding_dim = embedding_dim
        self._store: dict[str, dict[str, Any]] = {}
        self._embeddings: dict[str, list[float]] = {}

    def store(self, key: str, value: Any, text: str | None = None) -> None:
        content = text if text else str(value)
        embedding = _simple_hash_embedding(content, self._embedding_dim)
        self._store[key] = {
            "value": value,
            "text": content,
            "timestamp": time.time(),
        }
        self._embeddings[key] = embedding

    def retrieve(self, key: str) -> Any | None:
        entry = self._store.get(key)
        return entry.get("value") if entry else None

    def search(self, query: str, limit: int = 5,
               min_score: float = -1.0) -> list[dict[str, Any]]:
        query_emb = _simple_hash_embedding(query, self._embedding_dim)
        scores: list[tuple[str, float]] = []
        for key, emb in self._embeddings.items():
            score = _cosine_similarity(query_emb, emb)
            if score >= min_score:
                scores.append((key, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        results: list[dict[str, Any]] = []
        for key, score in scores[:limit]:
            entry = self._store.get(key, {})
            results.append({
                "key": key,
                "value": entry.get("value"),
                "score": round(score, 4),
                "text": entry.get("text", ""),
            })
        return results

    def remove(self, key: str) -> bool:
        removed = key in self._store
        self._store.pop(key, None)
        self._embeddings.pop(key, None)
        return removed

    def count(self) -> int:
        return len(self._store)

    def clear(self) -> None:
        self._store.clear()
        self._embeddings.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "count": len(self._store),
            "embedding_dim": self._embedding_dim,
        }
