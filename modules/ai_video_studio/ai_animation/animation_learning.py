"""Animation learning — learn preferred animation styles over time."""
from __future__ import annotations

from typing import Any


class AnimationLearning:
    """Records feedback and surfaces preferred actions/styles."""

    def __init__(self) -> None:
        self._feedback: dict[str, list[float]] = {}

    def record(self, action: str, score: float) -> None:
        if not 0 <= score <= 1:
            raise ValueError("score must be in [0, 1]")
        self._feedback.setdefault(action, []).append(score)

    def preferred_action(self) -> str | None:
        best: tuple[str, float] | None = None
        for action, scores in self._feedback.items():
            avg = sum(scores) / len(scores)
            if best is None or avg > best[1]:
                best = (action, avg)
        return best[0] if best else None

    def report(self) -> dict[str, Any]:
        return {
            action: {"count": len(scores), "average": round(sum(scores) / len(scores), 3)}
            for action, scores in self._feedback.items()
        }


_animation_learning: AnimationLearning | None = None


def get_animation_learning() -> AnimationLearning:
    global _animation_learning
    if _animation_learning is None:
        _animation_learning = AnimationLearning()
    return _animation_learning
