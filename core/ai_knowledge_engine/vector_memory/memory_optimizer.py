from __future__ import annotations

import time
import math
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class OptimizationStats:
    original_vectors: int = 0
    pruned_vectors: int = 0
    original_size_mb: float = 0.0
    optimized_size_mb: float = 0.0
    compression_ratio: float = 0.0
    time_taken_s: float = 0.0


class MemoryOptimizer:
    def __init__(self) -> None:
        self._optimization_history: list[OptimizationStats] = []

    def optimize(self, vectors: dict[str, list[float]]) -> dict[str, list[float]]:
        start = time.time()
        stats = OptimizationStats(
            original_vectors=len(vectors),
            original_size_mb=self._estimate_size(vectors),
        )
        optimized: dict[str, list[float]] = {}
        for vid, vec in vectors.items():
            quantized = [round(v, 6) for v in vec]
            optimized[vid] = quantized
        stats.optimized_size_mb = self._estimate_size(optimized)
        stats.pruned_vectors = stats.original_vectors - len(optimized)
        stats.compression_ratio = (
            (stats.original_size_mb - stats.optimized_size_mb) / stats.original_size_mb
            if stats.original_size_mb > 0 else 0.0
        )
        stats.time_taken_s = time.time() - start
        self._optimization_history.append(stats)
        return optimized

    def prune(self, vectors: dict[str, list[float]], threshold: float = 0.01) -> dict[str, list[float]]:
        start = time.time()
        stats = OptimizationStats(
            original_vectors=len(vectors),
            original_size_mb=self._estimate_size(vectors),
        )
        pruned: dict[str, list[float]] = {}
        for vid, vec in vectors.items():
            norm = math.sqrt(sum(v * v for v in vec))
            if norm >= threshold:
                pruned[vid] = vec
        stats.pruned_vectors = stats.original_vectors - len(pruned)
        stats.optimized_size_mb = self._estimate_size(pruned)
        stats.compression_ratio = (
            (stats.original_size_mb - stats.optimized_size_mb) / stats.original_size_mb
            if stats.original_size_mb > 0 else 0.0
        )
        stats.time_taken_s = time.time() - start
        self._optimization_history.append(stats)
        return pruned

    def compact(self, vectors: dict[str, list[float]]) -> dict[str, list[float]]:
        return self.optimize(vectors)

    def defragment(self, vectors: dict[str, list[float]]) -> dict[str, list[float]]:
        start = time.time()
        stats = OptimizationStats(
            original_vectors=len(vectors),
            original_size_mb=self._estimate_size(vectors),
        )
        sorted_keys = sorted(vectors.keys())
        defragged: dict[str, list[float]] = {k: vectors[k] for k in sorted_keys}
        stats.optimized_size_mb = self._estimate_size(defragged)
        stats.pruned_vectors = 0
        stats.compression_ratio = 0.0
        stats.time_taken_s = time.time() - start
        self._optimization_history.append(stats)
        return defragged

    def get_optimization_stats(self) -> list[OptimizationStats]:
        return list(self._optimization_history)

    def _estimate_size(self, vectors: dict[str, list[float]]) -> float:
        total_bytes = sum(len(v) * 8 for v in vectors.values())
        return total_bytes / (1024 * 1024)
