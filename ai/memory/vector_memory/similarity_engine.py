from __future__ import annotations

import math
from typing import List


class SimilarityEngine:
    """Computes similarity between vectors using various metrics."""

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            raise ValueError("Vector dimension mismatch")
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def euclidean_similarity(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            raise ValueError("Vector dimension mismatch")
        dist = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
        return 1.0 / (1.0 + dist)

    @staticmethod
    def dot_product(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            raise ValueError("Vector dimension mismatch")
        return sum(x * y for x, y in zip(a, b))

    @staticmethod
    def manhattan_similarity(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            raise ValueError("Vector dimension mismatch")
        dist = sum(abs(x - y) for x, y in zip(a, b))
        return 1.0 / (1.0 + dist)

    def compare(self, a: List[float], b: List[float], metric: str = "cosine") -> float:
        metric_map = {
            "cosine": self.cosine_similarity,
            "euclidean": self.euclidean_similarity,
            "dot": self.dot_product,
            "manhattan": self.manhattan_similarity,
        }
        fn = metric_map.get(metric)
        if fn is None:
            raise ValueError(f"Unknown metric: {metric}")
        return fn(a, b)
