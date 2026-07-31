"""Resource registry for cloud infrastructure (Volume 37, Fase 2)."""

from __future__ import annotations

from devops_engine.devops_models import (CloudProvider, Resource,
                                         ResourceStatus, ResourceType)
from devops_engine.devops_protocols import new_id, now


class ResourceManager:
    """Tracks generic cloud resources and their hourly cost."""

    def __init__(self) -> None:
        self._resources: dict[str, Resource] = {}

    def register(self, name: str,
                 kind: ResourceType = ResourceType.COMPUTE,
                 cost_per_hour: float = 0.0,
                 provider: CloudProvider | None = None,
                 region: str | None = None) -> Resource:
        resource = Resource(
            resource_id=new_id("resource"),
            name=name,
            kind=kind,
            provider=provider or CloudProvider.AWS,
            region=region or "us-east-1",
            status=ResourceStatus.RUNNING,
            cost_per_hour=float(cost_per_hour),
            created_at=now(),
        )
        self._resources[resource.resource_id] = resource
        return resource

    def get(self, resource_id: str) -> Resource | None:
        return self._resources.get(resource_id)

    def list(self) -> list[Resource]:
        return list(self._resources.values())

    def count(self) -> int:
        return len(self._resources)

    def release(self, resource_id: str) -> bool:
        resource = self._resources.get(resource_id)
        if resource is None:
            return False
        resource.status = ResourceStatus.TERMINATED
        return True

    def running_cost(self) -> float:
        return round(sum(r.cost_per_hour for r in self._resources.values()
                         if r.status == ResourceStatus.RUNNING), 2)
