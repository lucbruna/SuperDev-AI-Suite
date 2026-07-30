from __future__ import annotations

from typing import Any

from .reasoning_models import ReasoningResult


class ReasoningStatistics:
    """Statistical analysis of reasoning performance."""

    def __init__(self):
        self._results: list[ReasoningResult] = []

    def add_result(self, result: ReasoningResult) -> None:
        self._results.append(result)

    def average_confidence(self) -> float:
        if not self._results:
            return 0.0
        return sum(r.confidence for r in self._results) / len(self._results)

    def high_confidence_count(self, threshold: float = 0.8) -> int:
        return sum(1 for r in self._results if r.confidence >= threshold)

    def low_confidence_count(self, threshold: float = 0.3) -> int:
        return sum(1 for r in self._results if r.confidence < threshold)

    def summary(self) -> dict[str, Any]:
        return {
            "total": len(self._results),
            "avg_confidence": self.average_confidence(),
            "high_confidence": self.high_confidence_count(),
            "low_confidence": self.low_confidence_count(),
        }
