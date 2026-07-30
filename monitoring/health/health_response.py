from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..monitoring_models import HealthStatus


@dataclass
class HealthResponse:
    """Standardized health check response structure."""

    status: HealthStatus = HealthStatus.HEALTHY
    version: str = ""
    service: str = ""
    uptime_seconds: float = 0.0
    checks: dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "version": self.version,
            "service": self.service,
            "uptime_seconds": self.uptime_seconds,
            "checks": self.checks,
            "timestamp": self.timestamp,
        }

    def is_healthy(self) -> bool:
        return self.status == HealthStatus.HEALTHY

    @staticmethod
    def error(message: str) -> HealthResponse:
        return HealthResponse(
            status=HealthStatus.UNHEALTHY,
            checks={"error": message},
        )
