from __future__ import annotations

import time
from typing import Any

from .monitoring_models import HealthCheckResult, HealthStatus


class MonitoringHealth:
    """Central health check coordinator."""

    def __init__(self) -> None:
        self._checks: dict[str, Any] = {}

    def register(self, name: str, check: Any) -> None:
        self._checks[name] = check

    def unregister(self, name: str) -> None:
        self._checks.pop(name, None)

    async def check_all(self) -> dict[str, HealthCheckResult]:
        results: dict[str, HealthCheckResult] = {}
        for name, check in self._checks.items():
            try:
                start = time.monotonic()
                checker = getattr(check, "check", check)
                if callable(checker):
                    result = checker()
                    if hasattr(result, "__await__"):
                        result = await result
                else:
                    result = checker
                latency = round((time.monotonic() - start) * 1000, 2)
                if isinstance(result, HealthCheckResult):
                    results[name] = result
                else:
                    healthy = bool(result)
                    results[name] = HealthCheckResult(
                        component=name,
                        status=HealthStatus.HEALTHY if healthy else HealthStatus.UNHEALTHY,
                        latency_ms=latency,
                    )
            except Exception as exc:
                results[name] = HealthCheckResult(
                    component=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(exc),
                )
        return results

    async def is_healthy(self) -> bool:
        results = await self.check_all()
        return all(r.status == HealthStatus.HEALTHY for r in results.values())

    def list_checks(self) -> list[str]:
        return list(self._checks.keys())


__all__ = ["MonitoringHealth"]
