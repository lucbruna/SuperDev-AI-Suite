"""Performance tuning for agent operations."""
from __future__ import annotations

from typing import Any, Dict, List


class PerformanceTuner:
    """Tunes agent performance parameters based on metrics."""

    def __init__(self) -> None:
        self._tuning_history: List[Dict[str, Any]] = []
        self._parameters: Dict[str, float] = {
            "batch_size": 10.0,
            "cache_ttl": 300.0,
            "retry_limit": 3.0,
            "timeout_seconds": 30.0,
        }

    def tune(self, context: Dict[str, Any]) -> Dict[str, Any]:
        metrics = context.get("metrics", {})
        adjustments: Dict[str, str] = {}
        latency = float(metrics.get("avg_latency_ms", 0))
        if latency > 500:
            adjustments["timeout_seconds"] = "increased to 60"
            self._parameters["timeout_seconds"] = 60.0
        error_rate = float(metrics.get("error_rate", 0))
        if error_rate > 0.1:
            adjustments["retry_limit"] = "increased to 5"
            self._parameters["retry_limit"] = 5.0
        throughput = float(metrics.get("throughput", 0))
        if throughput > 100:
            adjustments["batch_size"] = "increased to 20"
            self._parameters["batch_size"] = 20.0
        result = {
            "parameters": dict(self._parameters),
            "adjustments": adjustments,
        }
        self._tuning_history.append(result)
        return result

    def get_parameters(self) -> Dict[str, float]:
        return dict(self._parameters)

    def set_parameter(self, name: str, value: float) -> None:
        self._parameters[name] = value
