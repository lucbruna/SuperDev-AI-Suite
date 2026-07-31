"""Anomaly detection."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid, statistics

class AnomalyPattern:
    def __init__(self, name: str, metric: str, threshold: float = 2.0) -> None:
        self.name = name
        self.metric = metric
        self.threshold = threshold
        self.baseline_values: List[float] = []

class AnomalyDetector:
    def __init__(self) -> None:
        self._patterns: Dict[str, AnomalyPattern] = {}
        self._anomalies: Dict[str, List[Dict[str, Any]]] = {}
        self._metrics: Dict[str, List[float]] = {}
    def add_pattern(self, name: str, metric: str, threshold: float = 2.0) -> AnomalyPattern:
        pattern = AnomalyPattern(name, metric, threshold)
        self._patterns[name] = pattern
        return pattern
    def record_metric(self, metric: str, value: float) -> None:
        self._metrics.setdefault(metric, []).append(value)
        self._check_anomalies(metric, value)
    def _check_anomalies(self, metric: str, value: float) -> None:
        for pattern in self._patterns.values():
            if pattern.metric == metric:
                values = self._metrics.get(metric, [])
                if len(values) > 10:
                    mean = statistics.mean(values[:-1])
                    stdev = statistics.stdev(values[:-1]) or 1.0
                    z_score = abs(value - mean) / stdev
                    if z_score > pattern.threshold:
                        anomaly = {"anomaly_id": str(uuid.uuid4())[:8], "pattern": pattern.name, "metric": metric, "value": value, "z_score": z_score, "timestamp": time.time()}
                        self._anomalies.setdefault(metric, []).append(anomaly)
    def get_anomalies(self, metric: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        if metric:
            return self._anomalies.get(metric, [])[-limit:]
        all_anomalies = []
        for anomalies in self._anomalies.values():
            all_anomalies.extend(anomalies)
        return sorted(all_anomalies, key=lambda x: x["timestamp"], reverse=True)[:limit]
    def get_baseline(self, metric: str) -> Dict[str, float]:
        values = self._metrics.get(metric, [])
        if not values:
            return {"mean": 0, "stdev": 0, "count": 0}
        return {"mean": statistics.mean(values), "stdev": statistics.stdev(values) if len(values) > 1 else 0, "count": len(values)}
    def clear_anomalies(self) -> int:
        n = sum(len(a) for a in self._anomalies.values())
        self._anomalies.clear()
        return n
