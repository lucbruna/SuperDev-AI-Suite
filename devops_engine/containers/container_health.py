"""Container health checks (Volume 37, Fase 2)."""

from __future__ import annotations

from devops_engine.devops_models import (Container, ContainerStatus,
                                         HealthCheckResult, HealthStatus)
from devops_engine.devops_protocols import new_id, now


class ContainerHealth:
    """Probes containers and summarizes fleet health."""

    def check(self, container: Container,
              latency_ms: float = 10.0) -> HealthCheckResult:
        healthy = (container.status == ContainerStatus.RUNNING
                   and bool(container.image))
        return HealthCheckResult(
            check_id=new_id("check"),
            target=container.name,
            status=HealthStatus.HEALTHY if healthy
            else HealthStatus.UNHEALTHY,
            latency_ms=latency_ms,
            checked_at=now(),
        )

    def is_healthy(self, container: Container) -> bool:
        return self.check(container).status == HealthStatus.HEALTHY

    def summary(self, containers: list[Container]) -> dict[str, int]:
        total = len(containers)
        healthy = sum(1 for container in containers
                      if self.is_healthy(container))
        return {"total": total, "healthy": healthy,
                "unhealthy": total - healthy}
