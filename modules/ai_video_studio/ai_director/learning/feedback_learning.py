"""Feedback learning — incorporates audience feedback into direction."""
from __future__ import annotations

from typing import Any


class FeedbackLearning:
    """Aggregates feedback signals."""

    def __init__(self) -> None:
        self._feedback: list[dict[str, Any]] = []

    def add(self, item: dict[str, Any]) -> None:
        self._feedback.append(item)

    def average_score(self) -> float:
        if not self._feedback:
            return 0.0
        return sum(item.get("score", 0.0) for item in self._feedback) / len(self._feedback)


_feedback_learning: FeedbackLearning | None = None


def get_feedback_learning() -> FeedbackLearning:
    global _feedback_learning
    if _feedback_learning is None:
        _feedback_learning = FeedbackLearning()
    return _feedback_learning
