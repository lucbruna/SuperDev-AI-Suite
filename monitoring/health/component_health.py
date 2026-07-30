from __future__ import annotations

import time
from typing import Any

from ..monitoring_models import HealthCheckResult, HealthStatus


class ComponentHealth:
    """Health check implementations for common components."""

    @staticmethod
    def ok(component: str, message: str = "OK") -> HealthCheckResult:
        return HealthCheckResult(component=component, status=HealthStatus.HEALTHY, message=message)

    @staticmethod
    def degraded(component: str, message: str = "Degraded") -> HealthCheckResult:
        return HealthCheckResult(component=component, status=HealthStatus.DEGRADED, message=message)

    @staticmethod
    def unhealthy(component: str, message: str = "Unhealthy") -> HealthCheckResult:
        return HealthCheckResult(component=component, status=HealthStatus.UNHEALTHY, message=message)

    @staticmethod
    def from_latency(component: str, latency_ms: float, warn_ms: float = 200, fail_ms: float = 1000) -> HealthCheckResult:
        if latency_ms >= fail_ms:
            return HealthCheckResult(
                component=component,
                status=HealthStatus.UNHEALTHY,
                latency_ms=latency_ms,
                message=f"High latency: {latency_ms:.0f}ms (threshold: {fail_ms:.0f}ms)",
            )
        if latency_ms >= warn_ms:
            return HealthCheckResult(
                component=component,
                status=HealthStatus.DEGRADED,
                latency_ms=latency_ms,
                message=f"Elevated latency: {latency_ms:.0f}ms (threshold: {warn_ms:.0f}ms)",
            )
        return HealthCheckResult(
            component=component,
            status=HealthStatus.HEALTHY,
            latency_ms=latency_ms,
            message=f"OK ({latency_ms:.0f}ms)",
        )

    @staticmethod
    def from_usage(component: str, usage_pct: float, warn_pct: float = 75, fail_pct: float = 90) -> HealthCheckResult:
        if usage_pct >= fail_pct:
            return ComponentHealth.unhealthy(component, f"Usage at {usage_pct:.0f}%")
        if usage_pct >= warn_pct:
            return ComponentHealth.degraded(component, f"Usage at {usage_pct:.0f}%")
        return ComponentHealth.ok(component, f"Usage at {usage_pct:.0f}%")
