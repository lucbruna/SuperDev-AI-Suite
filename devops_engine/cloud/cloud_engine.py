"""Cloud infrastructure engine (Volume 37, Fase 2)."""

from __future__ import annotations

from devops_engine.cloud.instance_manager import InstanceManager
from devops_engine.cloud.network_manager import Network, NetworkManager
from devops_engine.cloud.provider_manager import ProviderManager
from devops_engine.cloud.resource_manager import ResourceManager
from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_metrics import DevopsMetrics
from devops_engine.devops_models import (CloudProvider, Resource,
                                         ResourceType, Server)
from devops_engine.devops_security import DevopsSecurity


class CloudEngine:
    """Facade over cloud providers, instances, resources and networks."""

    def __init__(self, config: DevopsConfig | None = None,
                 events: DevopsEvents | None = None,
                 metrics: DevopsMetrics | None = None,
                 security: DevopsSecurity | None = None) -> None:
        self.config = config or DevopsConfig()
        self.events = events or DevopsEvents()
        self.metrics = metrics or DevopsMetrics()
        self.security = security or DevopsSecurity()
        self.providers = ProviderManager()
        self.instances = InstanceManager()
        self.resources = ResourceManager()
        self.networks = NetworkManager()

    def _resolve_provider(self, provider: CloudProvider | str | None
                          ) -> CloudProvider:
        if isinstance(provider, str):
            return self.providers.select(provider)
        return provider or self.config.provider

    def provision_server(self, name: str, cpu: int = 2, memory_gb: int = 4,
                         provider: CloudProvider | str | None = None,
                         region: str | None = None) -> Server:
        server = self.instances.provision(
            name, cpu, memory_gb, self._resolve_provider(provider), region)
        self.events.publish(DevopsEventType.RESOURCE_PROVISIONED,
                            {"server_id": server.server_id, "name": name})
        self.metrics.increment("devops.cloud.servers")
        return server

    def terminate_server(self, server_id: str, actor: str = "admin") -> bool:
        if not self.security.approve(actor):
            self.security.audit_deny(actor, server_id)
            return False
        if not self.instances.terminate(server_id):
            return False
        self.events.publish(DevopsEventType.RESOURCE_TERMINATED,
                            {"server_id": server_id, "actor": actor})
        return True

    def create_network(self, name: str, cidr: str = "10.0.0.0/16",
                       provider: CloudProvider | str | None = None,
                       region: str | None = None) -> Network:
        return self.networks.create(
            name, cidr, self._resolve_provider(provider), region)

    def delete_network(self, network_id: str, actor: str = "admin") -> bool:
        if not self.security.approve(actor):
            self.security.audit_deny(actor, network_id)
            return False
        return self.networks.delete(network_id)

    def register_resource(self, name: str,
                          kind: ResourceType = ResourceType.COMPUTE,
                          cost_per_hour: float = 0.0) -> Resource:
        return self.resources.register(
            name, kind, cost_per_hour,
            provider=self.config.provider, region=self.config.region)

    def release_resource(self, resource_id: str) -> bool:
        return self.resources.release(resource_id)

    def stats(self) -> dict[str, int | float]:
        return {
            "servers": self.instances.count(),
            "resources": self.resources.count(),
            "networks": self.networks.count(),
            "running_cost": self.resources.running_cost(),
        }
