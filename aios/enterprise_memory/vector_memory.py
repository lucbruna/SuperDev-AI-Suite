"""AIOS Vector Memory — embedding store with cosine similarity.

Vectors are sparse token-count maps (deterministic, dependency-free).
A ``featurize`` hook allows plugging a real embedding model later;
recall falls back to the built-in tokenizer.
"""

from __future__ import annotations

import math
import re
import time
import uuid
from typing import Any, Callable

_WORD_RE = re.compile(r"[a-zA-Z0-9_]+")

Featurizer = Callable[[Any], dict[str, float]]


def _default_featurize(text: Any) -> dict[str, float]:
    counts: dict[str, float] = {}
    for token in _WORD_RE.findall(str(text).lower()):
        counts[token] = counts.get(token, 0.0) + 1.0
    return counts


def _norm(vector: dict[str, float]) -> float:
    return math.sqrt(sum(v * v for v in vector.values()))


def cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    shared = set(a) & set(b)
    if not shared:
        return 0.0
    dot = sum(a[t] * b[t] for t in shared)
    denom = _norm(a) * _norm(b)
    if denom == 0.0:
        return 0.0
    return dot / denom


class VectorMemory:
    """Store of embedded records retrieved by similarity."""

    def __init__(self, featurizer: Featurizer | None = None, max_records: int = 10_000) -> None:
        self._featurizer = featurizer or _default_featurize
        self._records: list[dict[str, Any]] = []
        self._max = max_records

    def store(self, content: Any, **meta: Any) -> dict[str, Any]:
        embedding = self._featurizer(content)
        record = {
            "record_id": f"vec-{uuid.uuid4().hex[:10]}",
            "content": content,
            "embedding": embedding,
            "tags": list(meta.get("tags", [])),
            "timestamp": time.time(),
        }
        self._records.append(record)
        if len(self._records) > self._max:
            self._records = self._records[-self._max:]
        return record

    def recall(self, query: Any = None, limit: int = 5, **filters: Any) -> list[dict[str, Any]]:
        tags = set(filters.get("tags", []))
        if query is None:
            query_vec: dict[str, float] = {}
        elif isinstance(query, dict):
            query_vec = query
        else:
            query_vec = self._featurizer(query)
        scored = []
        for record in self._records:
            if tags and not tags.issubset(set(record["tags"])):
                continue
            score = cosine_similarity(query_vec, record["embedding"]) if query_vec else 1.0
            if score > 0.0:
                scored.append((score, record))
        scored.sort(key=lambda pair: -pair[0])
        return [dict(record, score=round(score, 4)) for score, record in scored[:limit]]

    def forget(self, record_id: str) -> bool:
        before = len(self._records)
        self._records = [r for r in self._records if r["record_id"] != record_id]
        return len(self._records) < before

    def clear(self) -> None:
        self._records.clear()

    def stats(self) -> dict[str, Any]:
        return {"records": len(self._records), "max": self._max}

    def snapshot(self) -> dict[str, Any]:
        return {"records": len(self._records), "max": self._max}
