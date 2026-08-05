"""Gesture learning — learns preferred gestures per context."""
from __future__ import annotations

from typing import Any


class GestureLearning:
    """Records gesture preference scores."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def record(self, gesture: str, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        self._scores.setdefault(gesture, []).append(score)

    def preferred(self) -> str | None:
        best: tuple[str, float] | None = None
        for gesture, scores in self._scores.items():
            avg = sum(scores) / len(scores)
            if best is None or avg > best[1]:
                best = (gesture, avg)
        return best[0] if best else None

    def report(self) -> dict[str, Any]:
        return {g: round(sum(s) / len(s), 3) for g, s in self._scores.items()}


_gesture_learning: GestureLearning | None = None


def get_gesture_learning() -> GestureLearning:
    global _gesture_learning
    if _gesture_learning is None:
        _gesture_learning = GestureLearning()
    return _gesture_learning
