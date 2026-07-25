from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """System health monitoring."""

    def __init__(self):
        self._checks: dict[str, Any] = {}
        self._results: list[ComponentHealth] = []

    def register_check(self, name: str, check_func) -> None:
        self._checks[name] = check_func

    async def check_all(self) -> list[ComponentHealth]:
        self._results = []
        for name, check_func in self._checks.items():
            try:
                result = await check_func()
                if isinstance(result, ComponentHealth):
                    self._results.append(result)
                else:
                    self._results.append(ComponentHealth(
                        name=name,
                        status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                    ))
            except Exception as e:
                self._results.append(ComponentHealth(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    error=str(e),
                ))
        return self._results

    def get_overall_status(self) -> HealthStatus:
        if not self._results:
            return HealthStatus.UNKNOWN
        statuses = [r.status for r in self._results]
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        if any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        return HealthStatus.DEGRADED


health_checker = HealthChecker()
