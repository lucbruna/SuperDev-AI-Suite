"""Docker runtime manager (Volume 37, Fase 2)."""

from __future__ import annotations

from devops_engine.devops_models import Container, ContainerStatus
from devops_engine.devops_protocols import new_id, now


class DockerManager:
    """Runs, stops and starts containers."""

    def __init__(self) -> None:
        self._containers: dict[str, Container] = {}

    def run(self, name: str, image: str, ports: list[int] | None = None,
            cpu: int = 1, memory_mb: int = 512) -> Container:
        container = Container(
            container_id=new_id("container"),
            name=name,
            image=image,
            status=ContainerStatus.RUNNING,
            ports=list(ports or []),
            cpu=cpu,
            memory_mb=memory_mb,
            created_at=now(),
        )
        self._containers[container.container_id] = container
        return container

    def stop(self, container_id: str) -> bool:
        container = self._containers.get(container_id)
        if container is None:
            return False
        container.status = ContainerStatus.STOPPED
        return True

    def start(self, container_id: str) -> bool:
        container = self._containers.get(container_id)
        if container is None:
            return False
        container.status = ContainerStatus.RUNNING
        return True

    def get(self, container_id: str) -> Container | None:
        return self._containers.get(container_id)

    def list(self) -> list[Container]:
        return list(self._containers.values())

    def count(self) -> int:
        return len(self._containers)
