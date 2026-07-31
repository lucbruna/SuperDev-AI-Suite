"""Bottleneck detection and resolution."""

from __future__ import annotations

from typing import Any


class BottleneckResolver:
    """Identifies and resolves performance bottlenecks."""

    def __init__(self) -> None:
        self._thresholds: dict[str, float] = {
            "latency_ms": 500.0,
            "error_rate": 0.1,
            "queue_depth": 50.0,
            "memory_usage_pct": 85.0,
        }

    def identify(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        bottlenecks: list[dict[str, Any]] = []
        for metric_name, threshold in self._thresholds.items():
            value = float(metrics.get(metric_name, 0))
            if value > threshold:
                severity = "critical" if value > threshold * 1.5 else "warning"
                bottlenecks.append(
                    {
                        "metric": metric_name,
                        "current_value": value,
                        "threshold": threshold,
                        "severity": severity,
                        "suggestion": self._suggest_resolution(metric_name, severity),
                    }
                )
        return bottlenecks

    def _suggest_resolution(self, metric: str, severity: str) -> str:
        suggestions = {
            "latency_ms": "Consider caching or parallelizing slow operations",
            "error_rate": "Review error logs and add retry logic with backoff",
            "queue_depth": "Increase worker count or optimize task throughput",
            "memory_usage_pct": "Implement memory cleanup or increase allocation",
        }
        base = suggestions.get(metric, "Investigate and optimize")
        if severity == "critical":
            return f"CRITICAL: {base} - immediate action required"
        return base

    def set_threshold(self, metric: str, threshold: float) -> None:
        self._thresholds[metric] = threshold
