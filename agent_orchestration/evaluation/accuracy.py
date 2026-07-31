"""Accuracy scoring for agent outputs (Volume 31)."""

from __future__ import annotations

from typing import Any


class AccuracyScorer:
    """Scores outputs against expected results and counts errors."""

    def __init__(self) -> None:
        self._errors: dict[str, int] = {}
        self._scores: dict[str, list[float]] = {}

    def score(self, agent_id: str, output: Any,
              expected: Any) -> float:
        value = 1.0 if output == expected else 0.0
        self._scores.setdefault(agent_id, []).append(value)
        if value == 0.0:
            self._errors[agent_id] = self._errors.get(agent_id, 0) + 1
        return value

    def accuracy(self, agent_id: str) -> float:
        scores = self._scores.get(agent_id, [])
        if not scores:
            return 0.0
        return sum(scores) / len(scores)

    def errors(self, agent_id: str) -> int:
        return self._errors.get(agent_id, 0)

    def count(self, agent_id: str) -> int:
        return len(self._scores.get(agent_id, []))
