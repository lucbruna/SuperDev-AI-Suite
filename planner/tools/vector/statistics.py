from __future__ import annotations

import math
from typing import Any


class VectorStatistics:
    """Statistical analysis of vector collections."""

    @staticmethod
    def mean(vectors: list[list[float]]) -> list[float]:
        if not vectors:
            return []
        dim = len(vectors[0])
        result = [0.0] * dim
        for vec in vectors:
            for i, v in enumerate(vec):
                result[i] += v
        return [v / len(vectors) for v in result]

    @staticmethod
    def std(vectors: list[list[float]]) -> list[float]:
        if not vectors or len(vectors) < 2:
            return []
        dim = len(vectors[0])
        mean = VectorStatistics.mean(vectors)
        variance = [0.0] * dim
        for vec in vectors:
            for i, v in enumerate(vec):
                variance[i] += (v - mean[i]) ** 2
        return [math.sqrt(v / (len(vectors) - 1)) for v in variance]

    @staticmethod
    def dimension_stats(vectors: list[list[float]]) -> dict[str, Any]:
        if not vectors:
            return {"count": 0, "dimension": 0}
        return {
            "count": len(vectors),
            "dimension": len(vectors[0]),
            "mean": VectorStatistics.mean(vectors),
            "std": VectorStatistics.std(vectors),
        }

    @staticmethod
    def magnitude_stats(vectors: list[list[float]]) -> dict[str, float]:
        magnitudes = [math.sqrt(sum(v * v for v in vec)) for vec in vectors]
        if not magnitudes:
            return {"min": 0.0, "max": 0.0, "mean": 0.0}
        return {
            "min": min(magnitudes),
            "max": max(magnitudes),
            "mean": sum(magnitudes) / len(magnitudes),
        }
