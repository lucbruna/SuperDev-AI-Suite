"""Metric analyzer for trend detection and insights."""

from __future__ import annotations

from typing import Any


class MetricAnalyzer:
    """Analyzes metric trends over time to detect patterns."""

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def record(self, metrics: dict[str, Any]) -> None:
        self._history.append(metrics)

    def analyze_trends(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        if not data:
            return {"trends": {}, "summary": "No data available"}
        numeric_keys: dict[str, list[float]] = {}
        for entry in data:
            for key, value in entry.items():
                if isinstance(value, (int, float)):
                    numeric_keys.setdefault(key, []).append(float(value))
        trends: dict[str, Any] = {}
        for key, values in numeric_keys.items():
            if len(values) < 2:
                trends[key] = {"direction": "stable", "avg": round(values[0], 3)}
                continue
            avg = sum(values) / len(values)
            first_half = values[: len(values) // 2]
            second_half = values[len(values) // 2 :]
            first_avg = sum(first_half) / max(len(first_half), 1)
            second_avg = sum(second_half) / max(len(second_half), 1)
            diff = second_avg - first_avg
            direction = "improving" if diff > 0.01 else "declining" if diff < -0.01 else "stable"
            trends[key] = {
                "direction": direction,
                "avg": round(avg, 3),
                "min": round(min(values), 3),
                "max": round(max(values), 3),
                "change": round(diff, 3),
            }
        improving = [k for k, v in trends.items() if v["direction"] == "improving"]
        declining = [k for k, v in trends.items() if v["direction"] == "declining"]
        return {
            "trends": trends,
            "summary": f"{len(improving)} improving, {len(declining)} declining out of {len(trends)} metrics",
            "improving": improving,
            "declining": declining,
        }

    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]
