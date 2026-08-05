"""Hallmark optimizer — adjust run parameters from observed outcomes."""
from __future__ import annotations
from typing import Any


class RunOptimizer:
    """Suggest parameter adjustments given prior outcomes."""

    def __init__(self, *, step: float = 0.1, bounds: tuple[float, float] = (0.0, 1.0)) -> None:
        self._step = step
        self._bounds = bounds

    def suggest(self, parameter: float, outcome_score: float) -> float:
        """Move ``parameter`` toward the bound that correlates with success."""
        low, high = self._bounds
        delta = self._step if outcome_score >= 0.5 else -self._step
        return max(low, min(high, parameter + delta))

    def analyze(self, runs: list[dict[str, Any]]) -> dict[str, Any]:
        """Summarize a list of runs with their parameter snapshots."""
        scores = [float(run.get("score", 0.0)) for run in runs]
        average = round(sum(scores) / len(scores), 3) if scores else 0.0
        return {
            "runs": len(runs),
            "average_score": average,
            "best_run": max(runs, key=lambda r: r.get("score", 0.0)) if runs else None,
        }
