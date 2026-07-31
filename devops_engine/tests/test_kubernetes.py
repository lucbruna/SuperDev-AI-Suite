"""Tests for the kubernetes subpackage (Volume 37, Fase 3)."""

from __future__ import annotations

import pytest

from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_models import (ClusterStatus, DeploymentStatus,
                                         PodStatus, ServiceStatus)
from devops_engine.kubernetes import KubeEngine


@pytest.fixture()
def kube() -> KubeEngine:
    return KubeEngine()


class TestClusterManager:
    def test_create(self, kube: KubeEngine) -> None:
        cluster = kube.clusters.create("prod", nodes=5)
        assert cluster.status == ClusterStatus.READY
        assert cluster.nodes == 5
        assert kube.clusters.count() == 1

    def test_degrade_and_remove(self, kube: KubeEngine) -> None:
        cluster = kube.clusters.create("prod")
        assert kube.clusters.degrade(cluster.cluster_id) is True
        assert cluster.status == ClusterStatus.DEGRADED
        assert kube.clusters.remove(cluster.cluster_id) is True
        assert cluster.status == ClusterStatus.DOWN
        assert kube.clusters.count() == 0


class TestDeploymentManager:
    def test_create_complete(self, kube: KubeEngine) -> None:
        deployment = kube.deployments.create("api", "api:1.0.0", replicas=3)
        assert deployment.status == DeploymentStatus.ROLLING
        assert kube.deployments.complete(deployment.deployment_id) is True
        assert deployment.status == DeploymentStatus.COMPLETED

    def test_scale(self, kube: KubeEngine) -> None:
        deployment = kube.deployments.create("api", "api:1.0.0")
        assert kube.deployments.scale(deployment.deployment_id, 10) is True
        assert deployment.desired == 10

    def test_scale_negative_rejected(self, kube: KubeEngine) -> None:
        deployment = kube.deployments.create("api", "api:1.0.0")
        assert kube.deployments.scale(deployment.deployment_id, -1) is False

    def test_rollback(self, kube: KubeEngine) -> None:
        deployment = kube.deployments.create("api", "api:1.0.0")
        assert kube.deployments.rollback(deployment.deployment_id) is True
        assert deployment.status == DeploymentStatus.ROLLED_BACK


class TestPodAndService:
    def test_pod(self, kube: KubeEngine) -> None:
        pod = kube.pods.create("web-1", "web:1.0.0", cluster_id="c1")
        assert pod.status == PodStatus.RUNNING
        assert kube.pods.fail(pod.pod_id) is True
        assert pod.status == PodStatus.FAILED

    def test_service(self, kube: KubeEngine) -> None:
        service = kube.services.create("web", "app=web", ports=[80, 443])
        assert service.status == ServiceStatus.ACTIVE
        assert service.ports == [80, 443]
        assert kube.services.remove(service.service_id) is True
        assert kube.services.count() == 0


class TestKubeEngine:
    def test_create_cluster_event(self, kube: KubeEngine) -> None:
        events = DevopsEvents()
        kube.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.CLUSTER_READY, seen.append)
        kube.create_cluster("prod")
        assert len(seen) == 1
        assert kube.metrics.count("devops.kube.clusters") == 1

    def test_deploy_flow(self, kube: KubeEngine) -> None:
        events = DevopsEvents()
        kube.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.DEPLOYMENT_COMPLETED, seen.append)
        deployment = kube.deploy("api", "api:2.0.0", replicas=4)
        assert deployment.status == DeploymentStatus.COMPLETED
        assert deployment.desired == 4
        assert len(seen) == 1
        assert kube.metrics.count("devops.kube.deployments") == 1

    def test_scale(self, kube: KubeEngine) -> None:
        deployment = kube.deploy("api", "api:1.0.0")
        assert kube.scale(deployment.deployment_id, 8) is True
        assert deployment.desired == 8

    def test_rollback_requires_approval(self, kube: KubeEngine) -> None:
        deployment = kube.deploy("api", "api:1.0.0")
        assert kube.rollback(deployment.deployment_id, "guest") is False
        assert kube.rollback(deployment.deployment_id, "admin") is True
        assert deployment.status == DeploymentStatus.ROLLED_BACK

    def test_expose(self, kube: KubeEngine) -> None:
        service = kube.expose("web", "app=web", ports=[80])
        assert service.status == ServiceStatus.ACTIVE
        assert kube.services.count() == 1

    def test_create_pod(self, kube: KubeEngine) -> None:
        pod = kube.create_pod("worker", "worker:1.0.0")
        assert pod.status == PodStatus.RUNNING

    def test_stats(self, kube: KubeEngine) -> None:
        kube.create_cluster("prod")
        kube.deploy("api", "api:1.0.0")
        assert kube.stats()["clusters"] == 1
        assert kube.stats()["deployments"] == 1
