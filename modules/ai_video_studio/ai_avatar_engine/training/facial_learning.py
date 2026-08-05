"""Facial learning — learns preferred emotional expression intensities."""
from __future__ import annotations

from typing import Any


class FacialLearning:
    """Records expression preference scores."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def record(self, emotion: str, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        self._scores.setdefault(emotion, []).append(score)

    def preferred(self) -> str | None:
        best: tuple[str, float] | None = None
        for emotion, scores in self._scores.items():
            avg = sum(scores) / len(scores)
            if best is None or avg > best[1]:
                best = (emotion, avg)
        return best[0] if best else None

    def report(self) -> dict[str, Any]:
        return {e: round(sum(s) / len(s), 3) for e, s in self._scores.items()}


_facial_learning: FacialLearning | None = None


def get_facial_learning() -> FacialLearning:
    global _facial_learning
    if _facial_learning is None:
        _facial_learning = FacialLearning()
    return _facial_learning
