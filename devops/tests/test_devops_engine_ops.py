"""Tests for the implemented DevOpsEngine build/provision/destroy/status operations."""

from __future__ import annotations

from devops.devops_engine import DevOpsEngine


class TestDevOpsEngineOps:
    def test_build_registers_service(self) -> None:
        engine = DevOpsEngine()
        result = engine.build("billing", version="v1.2.0", service_type="api")
        assert result["build_id"].startswith("build-")
        assert result["status"] == "built"
        assert result["service"] == "billing"
        assert result["version"] == "v1.2.0"
        assert result["tag"] == "billing:v1.2.0"
        assert any(s.name == "billing" for s in engine.services)
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("devops.builds", 0) >= 1

    def test_build_updates_existing_service(self) -> None:
        engine = DevOpsEngine()
        engine.build("billing", version="v1.0.0")
        engine.build("billing", version="v2.0.0")
        services = [s for s in engine.services if s.name == "billing"]
        assert len(services) == 1
        assert services[0].version == "v2.0.0"
        assert len(engine.status()["builds"]) == 2

    def test_provision_creates_resources(self) -> None:
        engine = DevOpsEngine()
        result = engine.provision("staging", resource_types=["compute", "database"])
        assert result["status"] == "provisioned"
        assert len(result["resources"]) == 2
        assert result["resources"][0]["type"] == "compute"
        status = engine.status("staging")
        assert status["environment_count"] == 1
        assert status["environments"]["staging"]["status"] == "provisioned"
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("devops.provisions", 0) >= 1

    def test_provision_defaults(self) -> None:
        engine = DevOpsEngine()
        result = engine.provision("dev")
        assert len(result["resources"]) == 3  # compute, storage, network
        assert result["resources"][0]["provider"] == engine.config.provider

    def test_destroy_removes_environment_and_resources(self) -> None:
        engine = DevOpsEngine()
        engine.provision("staging")
        result = engine.destroy("staging")
        assert result["destroyed"] is True
        assert result["status"] == "destroyed"
        assert "staging" not in engine.status()["environments"]
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("devops.destroys", 0) >= 1

    def test_destroy_unknown_environment(self) -> None:
        engine = DevOpsEngine()
        result = engine.destroy("ghost")
        assert result["destroyed"] is False
        assert result["status"] == "not_found"

    def test_status_aggregates_all(self) -> None:
        engine = DevOpsEngine()
        engine.build("billing", version="v1")
        engine.provision("staging")
        engine.deploy("billing", "staging", version="v1")
        status = engine.status()
        assert status["build_count"] == 1
        assert status["environment_count"] == 1
        assert status["count"] == 1
        assert status["services"] == ["billing"]

    def test_status_filter_by_environment(self) -> None:
        engine = DevOpsEngine()
        engine.provision("staging")
        engine.provision("production")
        staging = engine.status("staging")
        assert staging["environment_count"] == 1
        assert "staging" in staging["environments"]
        assert "production" not in staging["environments"]

    def test_factory_create_service(self) -> None:
        engine = DevOpsEngine()
        service = engine.factory.create_service("web", "web")
        assert service.name == "web"
        assert service.status == "created"
        assert any(s.name == "web" for s in engine.services)
        assert "web" in engine.manager.list_services()[0]["name"]

    def test_factory_create_resource(self) -> None:
        engine = DevOpsEngine()
        resource = engine.factory.create_resource("db-main", "database")
        assert resource["name"] == "db-main"
        assert resource["status"] == "created"
        assert engine.registry.size >= 1


class TestDevOpsManagerOps:
    def test_create_environment_delegates(self) -> None:
        engine = DevOpsEngine()
        result = engine.manager.create_environment("qa", {"resource_types": ["compute"]})
        assert result["status"] == "provisioned"
        assert "qa" in engine.manager.list_environments()

    def test_get_status_delegates(self) -> None:
        engine = DevOpsEngine()
        engine.provision("staging")
        status = engine.manager.get_status("staging")
        assert status["environment_count"] == 1

    def test_list_services(self) -> None:
        engine = DevOpsEngine()
        assert engine.manager.list_services() == []
        engine.build("api", version="v1")
        assert engine.manager.list_services()[0]["name"] == "api"
