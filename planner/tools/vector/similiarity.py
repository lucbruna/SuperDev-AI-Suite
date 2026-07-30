from __future__ import annotations

from typing import Any

from .cosine_similarity import CosineSimilarity


class Similarity:
    """Unified similarity computation interface."""

    def __init__(self, method: str = "cosine"):
        self._method = method
        self._cosine = CosineSimilarity()

    def compute(self, a: list[float], b: list[float]) -> float:
        if self._method == "cosine":
            return self._cosine.compute(a, b)
        return 0.0

    def set_method(self, method: str) -> None:
        self._method = method
