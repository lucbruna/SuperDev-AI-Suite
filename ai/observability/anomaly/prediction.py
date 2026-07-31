"""Anomaly prediction."""
from __future__ import annotations

import statistics


class AnomalyPredictor:
    def __init__(self) -> None:
        self._history: dict[str, list[float]] = {}
    def record(self, metric_name: str, value: float) -> None:
        self._history.setdefault(metric_name, []).append(value)
        if len(self._history[metric_name]) > 1000:
            self._history[metric_name] = self._history[metric_name][-1000:]
    def predict_next(self, metric_name: str) -> dict[str, float]:
        values = self._history.get(metric_name, [])
        if len(values) < 3:
            return {"predicted": 0, "confidence": 0}
        mean = statistics.mean(values[-10:])
        trend = (values[-1] - values[-min(10, len(values))]) / max(min(10, len(values)), 1)
        predicted = values[-1] + trend
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        confidence = max(0, 1 - (stdev / max(abs(mean), 1)))
        return {"predicted": predicted, "confidence": confidence}
    def predict_anomaly_probability(self, metric_name: str, value: float) -> float:
        values = self._history.get(metric_name, [])
        if len(values) < 10:
            return 0.0
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)
        if stdev == 0:
            return 0.0
        z = abs(value - mean) / stdev
        return min(z / 4.0, 1.0)
    def list_metrics(self) -> list[str]:
        return list(self._history.keys())
