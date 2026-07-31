"""Kubernetes service management (Volume 37, Fase 3)."""

from __future__ import annotations

from devops_engine.devops_models import Service, ServiceStatus
from devops_engine.devops_protocols import new_id, now


class ServiceManager:
    """Exposes workloads through services."""

    def __init__(self) -> None:
        self._services: dict[str, Service] = {}

    def create(self, name: str, selector: str,
               ports: list[int] | None = None,
               cluster_id: str = "") -> Service:
        service = Service(
            service_id=new_id("service"),
            name=name,
            cluster_id=cluster_id,
            selector=selector,
            ports=list(ports or []),
            status=ServiceStatus.ACTIVE,
            created_at=now(),
        )
        self._services[service.service_id] = service
        return service

    def remove(self, service_id: str) -> bool:
        service = self._services.get(service_id)
        if service is None:
            return False
        service.status = ServiceStatus.STOPPED
        del self._services[service_id]
        return True

    def get(self, service_id: str) -> Service | None:
        return self._services.get(service_id)

    def list(self) -> list[Service]:
        return list(self._services.values())

    def count(self) -> int:
        return len(self._services)
