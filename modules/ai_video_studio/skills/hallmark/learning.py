"""Hallmark learning — record outcomes and derive preferences."""
from __future__ import annotations
from typing import Any


class FeedbackLearner:
    """Track per-outcome scores and expose derived preferences."""

    def __init__(self) -> None:
        self._scores: dict[str, list[float]] = {}

    def record(self, outcome: str, score: float) -> None:
        self._scores.setdefault(outcome, []).append(score)

    def average(self, outcome: str) -> float:
        values = self._scores.get(outcome, [])
        return round(sum(values) / len(values), 3) if values else 0.0

    def preferences(self) -> dict[str, float]:
        """Return outcomes ranked by average score (descending)."""
        ranked = sorted(self._scores, key=self.average, reverse=True)
        return {outcome: self.average(outcome) for outcome in ranked}

    def reset(self) -> None:
        self._scores.clear()
