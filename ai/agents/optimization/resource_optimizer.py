"""Resource optimizer for memory, CPU, and network."""

from __future__ import annotations

from typing import Any


class ResourceOptimizer:
    """Optimizes resource allocation across agent systems."""

    def __init__(self) -> None:
        self._resource_limits: dict[str, float] = {
            "memory_mb": 512.0,
            "cpu_percent": 80.0,
            "network_mbps": 100.0,
        }

    def optimize(self, context: dict[str, Any]) -> dict[str, Any]:
        current = context.get("current_usage", {})
        actions: list[str] = []
        for resource, limit in self._resource_limits.items():
            usage = float(current.get(resource, 0))
            if usage > limit * 0.9:
                actions.append(f"High {resource} usage ({usage}/{limit}) - scaling recommended")
            elif usage > limit * 0.7:
                actions.append(f"Moderate {resource} usage ({usage}/{limit}) - monitoring")
        return {
            "actions": actions,
            "limits": dict(self._resource_limits),
            "current_usage": current,
        }

    def set_limit(self, resource: str, limit: float) -> None:
        self._resource_limits[resource] = limit

    def get_limits(self) -> dict[str, float]:
        return dict(self._resource_limits)
