"""Performance evaluator for agent metrics."""
from __future__ import annotations

from typing import Any


class PerformanceEvaluator:
    """Evaluates agent performance across multiple dimensions."""

    def __init__(self) -> None:
        self._weights: dict[str, float] = {
            "speed": 0.25,
            "accuracy": 0.30,
            "completeness": 0.25,
            "efficiency": 0.20,
        }

    def evaluate(self, metrics: dict[str, Any]) -> dict[str, Any]:
        scores: dict[str, float] = {}
        for dim, weight in self._weights.items():
            raw = metrics.get(dim, 0.5)
            if isinstance(raw, (int, float)):
                scores[dim] = round(min(max(float(raw), 0.0), 1.0) * weight, 3)
            else:
                scores[dim] = round(0.5 * weight, 3)
        total = round(sum(scores.values()), 3)
        return {
            "score": total,
            "dimensions": scores,
            "rating": self._rate(total),
        }

    def _rate(self, score: float) -> str:
        if score >= 0.8:
            return "excellent"
        if score >= 0.6:
            return "good"
        if score >= 0.4:
            return "average"
        return "needs_improvement"

    def set_weights(self, weights: dict[str, float]) -> None:
        self._weights.update(weights)
