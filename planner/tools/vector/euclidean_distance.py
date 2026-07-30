from __future__ import annotations

import math


class EuclideanDistance:
    """Euclidean distance computation."""

    @staticmethod
    def compute(a: list[float], b: list[float]) -> float:
        if len(a) != len(b) or not a:
            return float("inf")
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
