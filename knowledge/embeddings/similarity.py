from __future__ import annotations

import logging
import math


class Similarity:
    """Vector similarity functions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.similarity")

    @staticmethod
    def cosine(left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        norm_left = math.sqrt(sum(a * a for a in left)) or 1.0
        norm_right = math.sqrt(sum(b * b for b in right)) or 1.0
        return dot / (norm_left * norm_right)

    @staticmethod
    def dot_product(left: list[float], right: list[float]) -> float:
        if len(left) != len(right):
            return 0.0
        return sum(a * b for a, b in zip(left, right))

    @staticmethod
    def euclidean(left: list[float], right: list[float]) -> float:
        if len(left) != len(right):
            return float("inf")
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))

    @staticmethod
    def jaccard(left: set, right: set) -> float:
        union = left | right
        if not union:
            return 0.0
        return len(left & right) / len(union)
