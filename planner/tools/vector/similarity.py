from __future__ import annotations

import math
from typing import Any


class Similarity:
    """Similarity computation methods for vectors."""

    @staticmethod
    def cosine(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        return dot / (na * nb) if na and nb else 0.0

    @staticmethod
    def euclidean(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return float("inf")
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    @staticmethod
    def manhattan(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return float("inf")
        return sum(abs(x - y) for x, y in zip(a, b))

    @staticmethod
    def dot_product(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        return sum(x * y for x, y in zip(a, b))
