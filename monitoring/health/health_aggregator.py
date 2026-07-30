from __future__ import annotations

import time
from typing import Any

from ..monitoring_models import HealthCheckResult, HealthStatus


class HealthAggregator:
    """Aggregates health check results across multiple components."""

    def __init__(self) -> None:
        self._snapshots: list[dict[str, Any]] = []

    def aggregate(self, results: dict[str, HealthCheckResult]) -> dict[str, Any]:
        healthy = sum(1 for r in results.values() if r.status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in results.values() if r.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for r in results.values() if r.status == HealthStatus.UNHEALTHY)
        total = len(results)

        overall = HealthStatus.HEALTHY
        if unhealthy > 0:
            overall = HealthStatus.UNHEALTHY
        elif degraded > 0:
            overall = HealthStatus.DEGRADED

        avg_latency = sum(r.latency_ms for r in results.values()) / max(total, 1)

        snapshot = {
            "timestamp": time.time(),
            "overall": overall.value,
            "total": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "uptime_pct": round(healthy / max(total, 1) * 100, 1),
            "avg_latency_ms": round(avg_latency, 2),
            "components": {
                name: {
                    "status": r.status.value,
                    "latency_ms": round(r.latency_ms, 2),
                }
                for name, r in results.items()
            },
        }

        self._snapshots.append(snapshot)
        self._prune()
        return snapshot

    def get_history(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(self._snapshots[-limit:])

    def uptime(self, window_minutes: float = 60) -> dict[str, Any]:
        now = time.time()
        cutoff = now - (window_minutes * 60)
        recent = [s for s in self._snapshots if s["timestamp"] >= cutoff]

        if not recent:
            return {"uptime_pct": 100.0, "window_minutes": window_minutes}

        healthy_count = sum(1 for s in recent if s["overall"] == "healthy")
        return {
            "uptime_pct": round(healthy_count / len(recent) * 100, 1),
            "window_minutes": window_minutes,
            "samples": len(recent),
        }

    def _prune(self) -> None:
        max_snapshots = 10000
        if len(self._snapshots) > max_snapshots:
            self._snapshots = self._snapshots[-max_snapshots:]
