"""Container engine (Volume 37, Fase 2)."""

from __future__ import annotations

from devops_engine.containers.container_health import ContainerHealth
from devops_engine.containers.docker_manager import DockerManager
from devops_engine.containers.image_builder import ImageBuilder
from devops_engine.containers.registry_manager import RegistryManager
from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (Container, HealthCheckResult,
                                         Image)


class ContainerEngine:
    """Facade over image builds, containers, registry and health."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.docker = DockerManager()
        self.images = ImageBuilder()
        self.registry = RegistryManager()
        self.health = ContainerHealth()

    def build(self, name: str, tag: str = "latest",
              dockerfile: str = "") -> Image:
        image = self.images.build(name, tag, dockerfile)
        self.events.publish(DevopsEventType.IMAGE_BUILT,
                            {"image_id": image.image_id,
                             "image": f"{name}:{tag}"})
        self.metrics.increment("devops.container.images")
        return image

    def run(self, name: str, image: str,
            ports: list[int] | None = None) -> Container:
        container = self.docker.run(name, image, ports)
        self.events.publish(DevopsEventType.CONTAINER_CREATED,
                            {"container_id": container.container_id})
        self.events.publish(DevopsEventType.CONTAINER_STARTED,
                            {"container_id": container.container_id})
        self.metrics.increment("devops.container.running")
        return container

    def stop(self, container_id: str) -> bool:
        if not self.docker.stop(container_id):
            return False
        self.events.publish(DevopsEventType.CONTAINER_STOPPED,
                            {"container_id": container_id})
        return True

    def push(self, image: Image) -> bool:
        if not self.registry.push(image):
            return False
        self.events.publish(DevopsEventType.IMAGE_PUSHED,
                            {"image_id": image.image_id})
        return True

    def check_health(self, container: Container) -> HealthCheckResult:
        result = self.health.check(container)
        self.events.publish(DevopsEventType.HEALTH_CHECKED,
                            {"target": container.name,
                             "status": result.status.value})
        return result

    def stats(self) -> dict[str, int]:
        return {
            "containers": self.docker.count(),
            "images": self.images.count(),
            "registry": self.registry.count(),
        }
