from __future__ import annotations

import time
from typing import Any

from .vector_store import VectorStore


class Optimizer:
    """Optimizes vector store performance — pruning, normalization, reindexing."""

    def __init__(self, store: VectorStore):
        self._store = store
        self._last_optimized: float = 0.0
        self._optimization_count: int = 0

    @property
    def last_optimized(self) -> float:
        return self._last_optimized

    @property
    def optimization_count(self) -> int:
        return self._optimization_count

    def prune_low_importance(self, threshold: float = 0.1) -> int:
        removed = 0
        for vid in self._store.vector_ids:
            meta = self._store.get_metadata(vid)
            importance = meta.get("importance", 1.0)
            if importance < threshold:
                self._store.delete(vid)
                removed += 1
        self._optimization_count += 1
        self._last_optimized = time.time()
        return removed

    def normalize_vectors(self) -> int:
        import math

        normalized = 0
        for vid in self._store.vector_ids:
            vec = self._store.get(vid)
            if vec is None:
                continue
            norm = math.sqrt(sum(x * x for x in vec))
            if norm > 0:
                normalized_vec = [x / norm for x in vec]
                self._store.update(vid, normalized_vec, self._store.get_metadata(vid))
                normalized += 1
        self._optimization_count += 1
        self._last_optimized = time.time()
        return normalized

    def deduplicate(self, threshold: float = 0.99) -> int:
        from .similarity_engine import SimilarityEngine

        sim = SimilarityEngine()
        removed = 0
        vids = self._store.vector_ids
        for i in range(len(vids)):
            for j in range(i + 1, len(vids)):
                vi = self._store.get(vids[i])
                vj = self._store.get(vids[j])
                if vi is None or vj is None:
                    continue
                if sim.cosine_similarity(vi, vj) >= threshold:
                    self._store.delete(vids[j])
                    removed += 1
        self._optimization_count += 1
        self._last_optimized = time.time()
        return removed

    def stats(self) -> dict[str, Any]:
        return {
            "last_optimized": self._last_optimized,
            "optimization_count": self._optimization_count,
            "vector_count": self._store.count,
        }
