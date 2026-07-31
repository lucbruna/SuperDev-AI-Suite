"""Tests for the containers subpackage (Volume 37, Fase 2)."""

from __future__ import annotations

import pytest

from devops_engine.containers import ContainerEngine
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_models import (ContainerStatus, HealthStatus,
                                         ImageStatus)


@pytest.fixture()
def containers() -> ContainerEngine:
    return ContainerEngine()


class TestImageBuilder:
    def test_build(self, containers: ContainerEngine) -> None:
        image = containers.build("web", "1.0.0", "FROM nginx")
        assert image.status == ImageStatus.BUILT
        assert len(image.digest) == 12

    def test_tag(self, containers: ContainerEngine) -> None:
        image = containers.build("web")
        tagged = containers.images.tag(image, "stable")
        assert tagged.tag == "stable"
        assert tagged.digest == image.digest

    def test_count(self, containers: ContainerEngine) -> None:
        containers.build("web", "1.0.0")
        assert containers.images.count() == 1


class TestDockerManager:
    def test_run_stop_start(self, containers: ContainerEngine) -> None:
        container = containers.run("web", "web:1.0.0", ports=[80])
        assert container.status == ContainerStatus.RUNNING
        assert container.ports == [80]
        assert containers.stop(container.container_id) is True
        assert container.status == ContainerStatus.STOPPED
        assert containers.docker.start(container.container_id) is True
        assert container.status == ContainerStatus.RUNNING

    def test_stop_missing(self, containers: ContainerEngine) -> None:
        assert containers.stop("nope") is False

    def test_count(self, containers: ContainerEngine) -> None:
        containers.run("web", "img:1")
        assert containers.docker.count() == 1


class TestRegistry:
    def test_push_pull(self, containers: ContainerEngine) -> None:
        image = containers.build("app", "2.0.0")
        assert containers.push(image) is True
        assert image.status == ImageStatus.PUSHED
        pulled = containers.registry.pull("app", "2.0.0")
        assert pulled is image

    def test_pull_missing(self, containers: ContainerEngine) -> None:
        assert containers.registry.pull("ghost", "1.0.0") is None

    def test_list(self, containers: ContainerEngine) -> None:
        image = containers.build("app")
        containers.push(image)
        assert containers.registry.count() == 1


class TestContainerHealth:
    def test_healthy_running(self, containers: ContainerEngine) -> None:
        container = containers.run("web", "web:1.0.0")
        assert containers.health.is_healthy(container) is True

    def test_unhealthy_stopped(self, containers: ContainerEngine) -> None:
        container = containers.run("web", "web:1.0.0")
        containers.stop(container.container_id)
        assert containers.health.is_healthy(container) is False

    def test_summary(self, containers: ContainerEngine) -> None:
        running = containers.run("a", "img:1")
        stopped = containers.run("b", "img:1")
        containers.stop(stopped.container_id)
        summary = containers.health.summary(containers.docker.list())
        assert summary == {"total": 2, "healthy": 1, "unhealthy": 1}

    def test_check_result(self, containers: ContainerEngine) -> None:
        container = containers.run("web", "img:1")
        result = containers.health.check(container)
        assert result.status == HealthStatus.HEALTHY


class TestContainerEngine:
    def test_events(self, containers: ContainerEngine) -> None:
        events = DevopsEvents()
        containers.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.CONTAINER_STARTED, seen.append)
        containers.run("web", "img:1")
        assert len(seen) == 1

    def test_check_health_event(self, containers: ContainerEngine) -> None:
        container = containers.run("web", "img:1")
        result = containers.check_health(container)
        assert result.status == HealthStatus.HEALTHY

    def test_stats(self, containers: ContainerEngine) -> None:
        containers.build("app")
        containers.run("web", "app:latest")
        stats = containers.stats()
        assert stats["containers"] == 1
        assert stats["images"] == 1
        assert stats["registry"] == 0
