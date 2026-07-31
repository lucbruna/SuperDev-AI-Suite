"""Anomaly detector."""

from __future__ import annotations

import statistics


class StatisticalDetector:
    def __init__(self, sensitivity: float = 2.0) -> None:
        self._sensitivity = sensitivity
        self._history: dict[str, list[float]] = {}

    def record(self, metric_name: str, value: float) -> None:
        self._history.setdefault(metric_name, []).append(value)
        if len(self._history[metric_name]) > 1000:
            self._history[metric_name] = self._history[metric_name][-1000:]

    def check(self, metric_name: str, value: float) -> bool:
        values = self._history.get(metric_name, [])
        if len(values) < 10:
            return False
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        if stdev == 0:
            return False
        z_score = abs(value - mean) / stdev
        return z_score > self._sensitivity

    def get_stats(self, metric_name: str) -> dict[str, float]:
        values = self._history.get(metric_name, [])
        if not values:
            return {"mean": 0, "stdev": 0, "count": 0}
        return {
            "mean": statistics.mean(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "count": len(values),
        }

    def list_metrics(self) -> list[str]:
        return list(self._history.keys())

    def clear(self, metric_name: str = "") -> int:
        if metric_name:
            n = len(self._history.get(metric_name, []))
            self._history.pop(metric_name, None)
            return n
        n = sum(len(v) for v in self._history.values())
        self._history.clear()
        return n
