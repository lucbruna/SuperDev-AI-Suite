"""Baseline management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class BaselineManager:
    def __init__(self) -> None:
        self._baselines: Dict[str, Dict[str, Any]] = {}
    def set_baseline(self, metric_name: str, mean: float, std: float, min_val: float = 0, max_val: float = 0) -> Dict[str, Any]:
        baseline = {"metric": metric_name, "mean": mean, "std": std, "min": min_val, "max": max_val, "updated_at": time.time()}
        self._baselines[metric_name] = baseline
        return baseline
    def get_baseline(self, metric_name: str) -> Optional[Dict[str, Any]]:
        return self._baselines.get(metric_name)
    def update_from_data(self, metric_name: str, values: List[float]) -> Dict[str, Any]:
        import statistics
        if not values:
            return {"error": "no_data"}
        mean = statistics.mean(values)
        std = statistics.stdev(values) if len(values) > 1 else 0
        return self.set_baseline(metric_name, mean, std, min(values), max(values))
    def is_within_baseline(self, metric_name: str, value: float, multiplier: float = 2.0) -> bool:
        baseline = self._baselines.get(metric_name)
        if not baseline:
            return True
        lower = baseline["mean"] - multiplier * baseline["std"]
        upper = baseline["mean"] + multiplier * baseline["std"]
        return lower <= value <= upper
    def list_baselines(self) -> List[Dict[str, Any]]:
        return list(self._baselines.values())
    def remove_baseline(self, metric_name: str) -> bool:
        if metric_name in self._baselines:
            del self._baselines[metric_name]
            return True
        return False
