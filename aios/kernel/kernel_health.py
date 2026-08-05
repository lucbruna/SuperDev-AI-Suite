"""AIOS Kernel Health — aggregated health status of the platform.

Composes the kernel monitor plus a fixed set of platform health
signals (state, uptime, component/service counts) into a single
HealthReport.
"""

from __future__ import annotations

import time
from typing import Any

from .kernel_monitor import KernelMonitor

HEALTHY = "healthy"
DEGRADED = "degraded"
UNHEALTHY = "unhealthy"


class KernelHealth:
    """Health aggregation built on top of a KernelMonitor."""

    def __init__(self, kernel: Any, monitor: KernelMonitor) -> None:
        self._kernel = kernel
        self._monitor = monitor

    def check(self) -> dict[str, Any]:
        uptime = None
        if self._kernel.started_at is not None:
            uptime = round(time.time() - self._kernel.started_at, 3)
        state_ok = self._kernel.state == "running"
        components = self._monitor.report()
        statuses = list(components["checks"].values())
        errors = [s for s in statuses if s["status"] != "ok"]
        if not state_ok:
            overall = UNHEALTHY
        elif errors:
            overall = DEGRADED if len(errors) <= 2 else UNHEALTHY
        else:
            overall = HEALTHY
        return {
            "overall": overall,
            "kernel_state": self._kernel.state,
            "uptime_s": uptime,
            "components": components,
            "component_count": len(statuses),
            "failed_checks": [s.get("error") for s in errors],
        }

    def is_healthy(self) -> bool:
        return self.check()["overall"] == HEALTHY
