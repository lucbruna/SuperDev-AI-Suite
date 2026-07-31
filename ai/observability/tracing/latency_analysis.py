"""Latency analysis."""

from __future__ import annotations

import statistics
from typing import Any


class LatencyAnalyzer:
    def __init__(self) -> None:
        self._latencies: dict[str, list[float]] = {}

    def record(self, operation: str, latency_ms: float) -> None:
        self._latencies.setdefault(operation, []).append(latency_ms)
        if len(self._latencies[operation]) > 1000:
            self._latencies[operation] = self._latencies[operation][-1000:]

    def analyze(self, operation: str) -> dict[str, float]:
        values = self._latencies.get(operation, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0, "count": 0}
        sorted_vals = sorted(values)
        return {
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "p50": sorted_vals[len(sorted_vals) // 2],
            "p95": sorted_vals[int(len(sorted_vals) * 0.95)],
            "p99": sorted_vals[int(len(sorted_vals) * 0.99)],
            "count": len(values),
        }

    def get_slow_operations(self, threshold_ms: float = 1000) -> list[dict[str, Any]]:
        results = []
        for op, values in self._latencies.items():
            avg = sum(values) / len(values) if values else 0
            if avg > threshold_ms:
                results.append({"operation": op, "avg_ms": avg, "count": len(values)})
        return sorted(results, key=lambda x: x["avg_ms"], reverse=True)

    def list_operations(self) -> list[str]:
        return list(self._latencies.keys())

    def clear(self, operation: str = "") -> int:
        if operation:
            n = len(self._latencies.get(operation, []))
            self._latencies.pop(operation, None)
            return n
        n = sum(len(v) for v in self._latencies.values())
        self._latencies.clear()
        return n
