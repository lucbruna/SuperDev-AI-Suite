"""Anomaly scoring."""
from __future__ import annotations

from typing import Any


class AnomalyScorer:
    def __init__(self) -> None:
        self._scores: list[dict[str, Any]] = []
    def score(self, metric: str, value: float, baseline_mean: float, baseline_std: float) -> dict[str, Any]:
        z_score = 0 if baseline_std == 0 else abs(value - baseline_mean) / baseline_std
        severity = "low"
        if z_score > 3:
            severity = "critical"
        elif z_score > 2.5:
            severity = "high"
        elif z_score > 2:
            severity = "medium"
        result = {"metric": metric, "value": value, "z_score": z_score, "severity": severity}
        self._scores.append(result)
        return result
    def get_scores(self, severity: str = "", limit: int = 100) -> list[dict[str, Any]]:
        results = self._scores
        if severity:
            results = [s for s in results if s["severity"] == severity]
        return results[-limit:]
    def get_summary(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for s in self._scores:
            sev = s["severity"]
            summary[sev] = summary.get(sev, 0) + 1
        return summary
    def clear(self) -> int:
        n = len(self._scores)
        self._scores.clear()
        return n
