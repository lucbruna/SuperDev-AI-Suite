"""Kubernetes orchestration engine (Volume 37, Fase 3)."""

from __future__ import annotations

from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (CloudProvider, Cluster, Deployment,
                                         Pod, Service)
from devops_engine.devops_security import DevopsSecurity
from devops_engine.kubernetes.cluster_manager import ClusterManager
from devops_engine.kubernetes.deployment_manager import DeploymentManager
from devops_engine.kubernetes.pod_manager import PodManager
from devops_engine.kubernetes.service_manager import ServiceManager


class KubeEngine:
    """Facade over clusters, deployments, pods and services."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None,
                 security: DevopsSecurity | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.security = security or DevopsSecurity()
        self.clusters = ClusterManager()
        self.deployments = DeploymentManager()
        self.pods = PodManager()
        self.services = ServiceManager()

    def create_cluster(self, name: str, nodes: int = 3,
                       provider: CloudProvider | str | None = None,
                       region: str | None = None) -> Cluster:
        resolved = CloudProvider(provider) if isinstance(provider, str) \
            else provider or self.config.provider
        cluster = self.clusters.create(name, nodes, resolved, region)
        self.events.publish(DevopsEventType.CLUSTER_READY,
                            {"cluster_id": cluster.cluster_id,
                             "name": name})
        self.metrics.increment("devops.kube.clusters")
        return cluster

    def deploy(self, name: str, image: str, replicas: int = 1,
               cluster_id: str = "") -> Deployment:
        deployment = self.deployments.create(name, image, replicas,
                                             cluster_id)
        self.events.publish(DevopsEventType.DEPLOYMENT_CREATED,
                            {"deployment_id": deployment.deployment_id,
                             "name": name})
        self.deployments.complete(deployment.deployment_id)
        self.events.publish(DevopsEventType.DEPLOYMENT_COMPLETED,
                            {"deployment_id": deployment.deployment_id})
        self.metrics.increment("devops.kube.deployments")
        return deployment

    def scale(self, deployment_id: str, replicas: int) -> bool:
        return self.deployments.scale(deployment_id, replicas)

    def rollback(self, deployment_id: str, actor: str = "admin") -> bool:
        if not self.security.approve(actor):
            self.security.audit_deny(actor, deployment_id)
            return False
        if not self.deployments.rollback(deployment_id):
            return False
        self.events.publish(DevopsEventType.DEPLOYMENT_ROLLED_BACK,
                            {"deployment_id": deployment_id,
                             "actor": actor})
        return True

    def expose(self, name: str, selector: str,
               ports: list[int] | None = None,
               cluster_id: str = "") -> Service:
        service = self.services.create(name, selector, ports, cluster_id)
        self.events.publish(DevopsEventType.SERVICE_CREATED,
                            {"service_id": service.service_id,
                             "name": name})
        return service

    def create_pod(self, name: str, image: str,
                   cluster_id: str = "") -> Pod:
        return self.pods.create(name, image, cluster_id)

    def stats(self) -> dict[str, int]:
        return {
            "clusters": self.clusters.count(),
            "deployments": self.deployments.count(),
            "pods": self.pods.count(),
            "services": self.services.count(),
        }
