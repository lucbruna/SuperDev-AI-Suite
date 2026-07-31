"""Latency optimization."""
from __future__ import annotations

from typing import Any


class LatencyOptimizer:
    def __init__(self) -> None:
        self._measurements: list[dict[str, Any]] = []
        self._targets: dict[str, float] = {}
    def set_target(self, operation: str, target_ms: float) -> dict[str, Any]:
        self._targets[operation] = target_ms
        return {"operation": operation, "target_ms": target_ms}
    def measure(self, operation: str, latency_ms: float) -> dict[str, Any]:
        target = self._targets.get(operation, 1000)
        within_target = latency_ms <= target
        entry = {"operation": operation, "latency_ms": latency_ms, "target_ms": target, "within_target": within_target}
        self._measurements.append(entry)
        return entry
    def average_latency(self, operation: str = "") -> float:
        if operation:
            measurements = [m for m in self._measurements if m["operation"] == operation]
        else:
            measurements = self._measurements
        if not measurements:
            return 0.0
        return sum(m["latency_ms"] for m in measurements) / len(measurements)
    def slowest_operations(self, count: int = 5) -> list[dict[str, Any]]:
        return sorted(self._measurements, key=lambda m: m["latency_ms"], reverse=True)[:count]
    def optimize_suggestions(self, operation: str) -> list[str]:
        avg = self.average_latency(operation)
        target = self._targets.get(operation, 1000)
        suggestions = []
        if avg > target:
            suggestions.append(f"Average latency ({avg:.0f}ms) exceeds target ({target:.0f}ms)")
            suggestions.append("Consider caching or batching")
        return suggestions
    def get_measurements(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._measurements[-limit:]
    def count(self) -> int:
        return len(self._measurements)
