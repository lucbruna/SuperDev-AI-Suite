"""Tests for the cloud infrastructure subpackage (Volume 37, Fase 2)."""

from __future__ import annotations

import pytest

from devops_engine.cloud import CloudEngine, Network
from devops_engine.cloud.provider_manager import ProviderManager
from devops_engine.devops_events import DevopsEventType, DevopsEvents
from devops_engine.devops_models import (CloudProvider, ResourceStatus,
                                         ResourceType)


@pytest.fixture()
def cloud() -> CloudEngine:
    return CloudEngine()


class TestProviderManager:
    def test_select_by_value(self) -> None:
        manager = ProviderManager()
        assert manager.select("gcp") == CloudProvider.GCP
        assert manager.select("ORACLE") == CloudProvider.ORACLE

    def test_select_unknown_falls_back(self) -> None:
        assert ProviderManager().select("darkcloud") == CloudProvider.PRIVATE

    def test_cost_factor(self) -> None:
        assert ProviderManager().cost_factor(CloudProvider.AWS) == 1.0

    def test_default_region(self) -> None:
        assert ProviderManager().default_region(CloudProvider.AWS) \
            == "us-east-1"

    def test_list_providers(self) -> None:
        assert CloudProvider.AWS in ProviderManager().list_providers()


class TestCloudEngine:
    def test_provision_server(self, cloud: CloudEngine) -> None:
        events = DevopsEvents()
        cloud.events = events
        seen: list[dict] = []
        events.on(DevopsEventType.RESOURCE_PROVISIONED, seen.append)
        server = cloud.provision_server("api", cpu=8, memory_gb=32)
        assert server.status == ResourceStatus.RUNNING
        assert server.cpu == 8
        assert cloud.instances.count() == 1
        assert len(seen) == 1

    def test_provision_with_string_provider(self, cloud: CloudEngine) -> None:
        server = cloud.provision_server("api", provider="gcp")
        assert server.provider == CloudProvider.GCP

    def test_terminate_with_approver(self, cloud: CloudEngine) -> None:
        server = cloud.provision_server("db")
        assert cloud.terminate_server(server.server_id, "admin") is True
        assert server.status == ResourceStatus.TERMINATED

    def test_terminate_denied_for_guest(self, cloud: CloudEngine) -> None:
        server = cloud.provision_server("db")
        assert cloud.terminate_server(server.server_id, "guest") is False
        assert server.status == ResourceStatus.RUNNING

    def test_terminate_missing(self, cloud: CloudEngine) -> None:
        assert cloud.terminate_server("nope", "admin") is False

    def test_networks(self, cloud: CloudEngine) -> None:
        network = cloud.create_network("prod", "10.0.0.0/16")
        assert isinstance(network, Network)
        assert network.cidr == "10.0.0.0/16"
        assert cloud.networks.count() == 1
        assert cloud.delete_network(network.network_id, "admin") is True
        assert cloud.networks.count() == 0

    def test_delete_network_denied(self, cloud: CloudEngine) -> None:
        network = cloud.create_network("prod")
        assert cloud.delete_network(network.network_id, "guest") is False
        assert cloud.networks.count() == 1

    def test_add_subnet(self, cloud: CloudEngine) -> None:
        network = cloud.create_network("prod")
        assert cloud.networks.add_subnet(network.network_id,
                                         "10.0.1.0/24") is True
        assert network.subnets == ["10.0.1.0/24"]

    def test_resources_and_cost(self, cloud: CloudEngine) -> None:
        resource = cloud.register_resource("postgres",
                                           ResourceType.DATABASE, 0.5)
        assert resource.kind == ResourceType.DATABASE
        assert cloud.resources.running_cost() == 0.5
        assert cloud.release_resource(resource.resource_id) is True
        assert resource.status == ResourceStatus.TERMINATED
        assert cloud.resources.running_cost() == 0.0

    def test_stats(self, cloud: CloudEngine) -> None:
        cloud.provision_server("api")
        assert cloud.stats()["servers"] == 1

    def test_metrics(self, cloud: CloudEngine) -> None:
        cloud.provision_server("api")
        assert cloud.metrics.count("devops.cloud.servers") == 1
