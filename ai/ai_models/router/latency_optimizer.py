"""Latency optimizer."""
from __future__ import annotations
from typing import Any, Dict, List

class LatencyOptimizer:
    def __init__(self) -> None:
        self._latencies: Dict[str, List[float]] = {}
    def record(self, model_id: str, latency_ms: float) -> None:
        self._latencies.setdefault(model_id, []).append(latency_ms)
        if len(self._latencies[model_id]) > 100:
            self._latencies[model_id] = self._latencies[model_id][-100:]
    def get_average(self, model_id: str) -> float:
        values = self._latencies.get(model_id, [])
        return sum(values) / len(values) if values else 0.0
    def get_p95(self, model_id: str) -> float:
        values = sorted(self._latencies.get(model_id, []))
        if not values:
            return 0.0
        idx = int(len(values) * 0.95)
        return values[min(idx, len(values)-1)]
    def fastest_model(self, task_type: str = "") -> str:
        averages = {mid: self.get_average(mid) for mid in self._latencies}
        if not averages:
            return ""
        return min(averages, key=averages.get)
    def compare(self, model_ids: List[str]) -> List[Dict[str, Any]]:
        return [{"model_id": mid, "avg_ms": self.get_average(mid), "p95_ms": self.get_p95(mid)} for mid in model_ids]
    def list_models(self) -> List[str]:
        return list(self._latencies.keys())
    def clear(self, model_id: str = "") -> int:
        if model_id:
            n = len(self._latencies.get(model_id, []))
            self._latencies.pop(model_id, None)
            return n
        n = sum(len(v) for v in self._latencies.values())
        self._latencies.clear()
        return n
