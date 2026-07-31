"""Performance optimizer."""
from __future__ import annotations
from typing import Any, Dict, List

class PerformanceOptimizer:
    def __init__(self) -> None:
        self._metrics: Dict[str, List[float]] = {}
        self._optimizations: List[Dict[str, Any]] = []
    def record(self, metric_name: str, value: float) -> None:
        self._metrics.setdefault(metric_name, []).append(value)
    def analyze(self, metric_name: str) -> Dict[str, Any]:
        values = self._metrics.get(metric_name, [])
        if not values:
            return {"error": "no_data"}
        return {"metric": metric_name, "min": min(values), "max": max(values), "avg": sum(values)/len(values), "trend": "up" if len(values) > 1 and values[-1] > values[0] else "down"}
    def optimize(self, target_metric: str, target_value: float) -> Dict[str, Any]:
        current = self.analyze(target_metric)
        if "error" in current:
            return current
        gap = target_value - current["avg"]
        suggestion = "increase" if gap > 0 else "decrease"
        result = {"metric": target_metric, "current": current["avg"], "target": target_value, "gap": gap, "suggestion": suggestion}
        self._optimizations.append(result)
        return result
    def get_optimizations(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._optimizations[-limit:]
    def list_metrics(self) -> List[str]:
        return list(self._metrics.keys())
    def count(self) -> int:
        return len(self._metrics)
