"""Anomaly Detection — flags outliers via z-score."""
from __future__ import annotations

import math
from typing import Any


class AnomalyDetection:
    """Detects outliers in a numeric series (|z| > threshold)."""

    def detect(self, series: list[float], *, threshold: float = 2.0) -> dict[str, Any]:
        if not series:
            return {"anomalies": [], "count": 0}
        mean = sum(series) / len(series)
        var = sum((v - mean) ** 2 for v in series) / len(series)
        std = math.sqrt(var) or 1.0
        anomalies = [
            {"index": i, "value": v, "z": round((v - mean) / std, 3)}
            for i, v in enumerate(series) if abs((v - mean) / std) > threshold
        ]
        return {"anomalies": anomalies, "count": len(anomalies), "mean": round(mean, 3)}


_anomaly_detection: AnomalyDetection | None = None


def get_anomaly_detection() -> AnomalyDetection:
    global _anomaly_detection
    if _anomaly_detection is None:
        _anomaly_detection = AnomalyDetection()
    return _anomaly_detection
