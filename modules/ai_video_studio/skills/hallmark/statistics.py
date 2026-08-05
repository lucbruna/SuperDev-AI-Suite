"""Hallmark statistics — aggregate run metrics."""
from __future__ import annotations
from typing import Any


class RunStatistics:
    """Record per-run durations and success flags; report aggregates."""

    def __init__(self) -> None:
        self.runs: list[dict[str, Any]] = []

    def record(self, *, duration_s: float, ok: bool, **extra: Any) -> None:
        self.runs.append({"duration_s": duration_s, "ok": ok, **extra})

    def aggregate(self) -> dict[str, Any]:
        """Return total runs, success rate, and average duration."""
        if not self.runs:
            return {"runs": 0, "success_rate": 0.0, "avg_duration_s": 0.0}
        total = len(self.runs)
        successes = sum(1 for run in self.runs if run["ok"])
        average = sum(run["duration_s"] for run in self.runs) / total
        return {
            "runs": total,
            "success_rate": round(successes / total, 3),
            "avg_duration_s": round(average, 3),
        }
