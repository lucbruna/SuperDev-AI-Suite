"""Project progress metrics."""

from __future__ import annotations

from typing import Any


class ProjectMetrics:
    """Computes progress, task distribution and risk signals."""

    def __init__(self, project_id: str) -> None:
        self.project_id = project_id
        self._weights: dict[str, float] = {}

    def set_weight(self, label: str, weight: float) -> None:
        self._weights[label] = max(0.0, min(1.0, weight))

    def progress(self, done_weights: float, total_weights: float) -> float:
        if total_weights <= 0:
            return 0.0
        return round(done_weights / total_weights * 100.0, 1)

    def distribution(self, total: int,
                     done: int, in_progress: int,
                     blocked: int) -> dict[str, Any]:
        base: dict[str, Any] = {"total": total, "done": done,
                                "in_progress": in_progress,
                                "blocked": blocked}
        base["pct_done"] = round(done / total * 100, 1) if total else 0.0
        base["pct_blocked"] = round(blocked / total * 100, 1) if total else 0.0
        return base

    def risk(self, blocked: int, overdue: int, total: int) -> str:
        if total == 0:
            return "low"
        score = (blocked * 2 + overdue) / total
        if score >= 0.5:
            return "high"
        if score >= 0.2:
            return "medium"
        return "low"

    def summary(self) -> dict[str, Any]:
        return {"project_id": self.project_id,
                "weights": dict(self._weights)}
