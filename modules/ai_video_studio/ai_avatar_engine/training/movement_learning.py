"""Movement learning — learns preferred movement styles."""
from __future__ import annotations

from typing import Any


class MovementLearning:
    """Records movement-style preference scores."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def record(self, style: str, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        self._scores.setdefault(style, []).append(score)

    def preferred(self) -> str | None:
        best: tuple[str, float] | None = None
        for style, scores in self._scores.items():
            avg = sum(scores) / len(scores)
            if best is None or avg > best[1]:
                best = (style, avg)
        return best[0] if best else None

    def report(self) -> dict[str, Any]:
        return {s: round(sum(v) / len(v), 3) for s, v in self._scores.items()}


_movement_learning: MovementLearning | None = None


def get_movement_learning() -> MovementLearning:
    global _movement_learning
    if _movement_learning is None:
        _movement_learning = MovementLearning()
    return _movement_learning
