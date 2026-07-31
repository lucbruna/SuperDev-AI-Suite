"""Virtual network management (Volume 37, Fase 2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from devops_engine.devops_models import CloudProvider, ResourceStatus
from devops_engine.devops_protocols import new_id, now


@dataclass
class Network:
    """A virtual private cloud network with subnets."""
    network_id: str
    name: str
    cidr: str = "10.0.0.0/16"
    provider: CloudProvider = CloudProvider.AWS
    region: str = "us-east-1"
    status: ResourceStatus = ResourceStatus.RUNNING
    subnets: list[str] = field(default_factory=list)
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class NetworkManager:
    """Creates and tears down virtual networks."""

    def __init__(self) -> None:
        self._networks: dict[str, Network] = {}

    def create(self, name: str, cidr: str = "10.0.0.0/16",
               provider: CloudProvider | None = None,
               region: str | None = None) -> Network:
        network = Network(
            network_id=new_id("network"),
            name=name,
            cidr=cidr,
            provider=provider or CloudProvider.AWS,
            region=region or "us-east-1",
            created_at=now(),
        )
        self._networks[network.network_id] = network
        return network

    def get(self, network_id: str) -> Network | None:
        return self._networks.get(network_id)

    def list(self) -> list[Network]:
        return list(self._networks.values())

    def count(self) -> int:
        return len(self._networks)

    def add_subnet(self, network_id: str, cidr: str) -> bool:
        network = self._networks.get(network_id)
        if network is None:
            return False
        network.subnets.append(cidr)
        return True

    def delete(self, network_id: str) -> bool:
        network = self._networks.get(network_id)
        if network is None:
            return False
        network.status = ResourceStatus.TERMINATED
        del self._networks[network_id]
        return True
