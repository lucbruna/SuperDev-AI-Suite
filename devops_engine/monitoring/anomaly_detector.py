"""Anomaly detection for monitoring (Volume 37, Fase 4)."""

from __future__ import annotations


class AnomalyDetector:
    """Detects outliers in metric series using a z-score heuristic."""

    def z_score(self, value: float, history: list[float]) -> float:
        if not history:
            return 0.0
        mean = sum(history) / len(history)
        if len(history) < 2:
            return 0.0
        variance = sum((item - mean) ** 2 for item in history) \
            / len(history)
        std = variance ** 0.5
        if std == 0.0:
            return 0.0
        return abs(value - mean) / std

    def score(self, values: list[float]) -> float:
        """Returns the anomaly score of the last sample."""
        if len(values) < 2:
            return 0.0
        return self.z_score(values[-1], values[:-1])

    def detect(self, values: list[float], threshold: float = 3.0) -> bool:
        """True when the last value is far above its history."""
        if len(values) < 3:
            return False
        return self.score(values) > threshold
