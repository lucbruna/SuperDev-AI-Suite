"""Composite quality scoring (Volume 31)."""

from __future__ import annotations

from typing import Any


class QualityScorer:
    """Blends accuracy, error count and latency into a 0-1 score."""

    def __init__(self, max_errors: int = 10,
                 time_baseline: float = 5.0) -> None:
        self.max_errors = max_errors
        self.time_baseline = time_baseline

    def score(self, accuracy: float, errors: int,
              avg_time: float) -> float:
        accuracy_component = max(0.0, min(1.0, accuracy))
        error_component = max(0.0, 1.0 - errors / self.max_errors)
        time_component = max(0.0, 1.0 - avg_time / self.time_baseline)
        return round(0.5 * accuracy_component
                     + 0.3 * error_component
                     + 0.2 * time_component, 4)

    @staticmethod
    def label(score: float) -> str:
        if score >= 0.9:
            return "excellent"
        if score >= 0.7:
            return "good"
        if score >= 0.5:
            return "acceptable"
        return "poor"
