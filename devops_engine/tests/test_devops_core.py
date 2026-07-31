"""Tests for the DevOps Engine core (Volume 37, Fase 1)."""

from __future__ import annotations

import pytest

from devops_engine.devops_config import DevopsConfig
from devops_engine.devops_engine import DevopsEngine
from devops_engine.devops_events import (DevopsEventType, DevopsEvents)
from devops_engine.devops_factory import build_devops_engine
from devops_engine.devops_manager import DevopsManager
from devops_engine.devops_models import (CloudProvider, Container,
                                         ContainerStatus, CostRecord,
                                         DeploymentStatus, HealthStatus,
                                         IncidentStatus, PipelineStatus,
                                         Resource, ResourceStatus,
                                         ResourceType, RestoreStatus,
                                         RiskLevel, Server, Severity)
from devops_engine.devops_protocols import (coerce_bool, coerce_number,
                                            new_id, normalize, rate,
                                            round_money, safe_get, tokenize,
                                            top_n)
from devops_engine.devops_registry import DevopsRegistry


@pytest.fixture()
def engine() -> DevopsEngine:
    return build_devops_engine()


class TestConfig:
    def test_defaults_and_get(self) -> None:
        config = DevopsConfig()
        assert config.provider == CloudProvider.AWS
        assert config.region == "us-east-1"
        assert config.get("env") == "production"
        assert config.get("missing", "x") == "x"

    def test_overrides_and_snapshot(self) -> None:
        config = DevopsConfig({"region": "sa-east-1", "env": "staging"})
        snapshot = config.snapshot()
        assert snapshot["region"] == "sa-east-1"
        assert snapshot["env"] == "staging"

    def test_provider_coercion(self) -> None:
        config = DevopsConfig({"provider": "gcp"})
        assert config.provider == CloudProvider.GCP

    def test_merge(self) -> None:
        config = DevopsConfig({"region": "sa-east-1"})
        merged = config.merge({"env": "drill"})
        assert merged.region == "sa-east-1"
        assert merged.env == "drill"


class TestEvents:
    def test_on_publish_off(self) -> None:
        events = DevopsEvents()
        seen: list[dict] = []
        listener = seen.append
        events.on(DevopsEventType.RESOURCE_PROVISIONED, listener)
        events.publish(DevopsEventType.RESOURCE_PROVISIONED, {"x": 1})
        events.off(DevopsEventType.RESOURCE_PROVISIONED, listener)
        events.publish(DevopsEventType.RESOURCE_PROVISIONED, {"x": 2})
        assert len(seen) == 1

    def test_once(self) -> None:
        events = DevopsEvents()
        seen: list[dict] = []
        events.once(DevopsEventType.INCIDENT_DETECTED, seen.append)
        events.publish(DevopsEventType.INCIDENT_DETECTED, {"a": 1})
        events.publish(DevopsEventType.INCIDENT_DETECTED, {"a": 2})
        assert len(seen) == 1

    def test_listener_isolation(self) -> None:
        events = DevopsEvents()

        def boom(_payload: dict) -> None:
            raise RuntimeError("boom")

        seen: list[dict] = []
        events.on(DevopsEventType.LOG_COLLECTED, boom)
        events.on(DevopsEventType.LOG_COLLECTED, seen.append)
        events.publish(DevopsEventType.LOG_COLLECTED, {"ok": True})
        assert len(seen) == 1


class TestProtocols:
    def test_new_id_prefix(self) -> None:
        assert new_id("server").startswith("server-")

    def test_coerce(self) -> None:
        assert coerce_bool("yes") is True
        assert coerce_bool(0) is False
        assert coerce_number("12.5") == 12.5
        assert coerce_number("bad", default=1.0) == 1.0

    def test_round_money(self) -> None:
        assert round_money(10.005) == 10.01
        assert round_money("7.5") == 7.5

    def test_text_helpers(self) -> None:
        assert normalize("  a   b ") == "a b"
        assert tokenize("API gateway failed") == ["api", "gateway",
                                                  "failed"]

    def test_safe_get(self) -> None:
        data = {"a": {"b": {"c": 42}}}
        assert safe_get(data, "a.b.c") == 42
        assert safe_get(data, "a.z", default=-1) == -1

    def test_top_n(self) -> None:
        assert top_n([3, 1, 2], key=lambda x: x, limit=2) == [3, 2]

    def test_rate(self) -> None:
        assert rate(5, 10) == 0.5
        assert rate(3, 0) == 0.0
        assert rate(15, 10) == 1.0


class TestModels:
    def test_server_defaults(self) -> None:
        server = Server(server_id="s1", name="app")
        assert server.cpu == 2
        assert server.status == ResourceStatus.PROVISIONING

    def test_resource_roundtrip(self) -> None:
        resource = Resource(resource_id="r1", name="db",
                            kind=ResourceType.DATABASE)
        assert resource.kind == ResourceType.DATABASE

    def test_container_defaults(self) -> None:
        container = Container(container_id="c1", name="web")
        assert container.status == ContainerStatus.CREATED
        assert container.memory_mb == 512

    def test_risk_rank(self) -> None:
        assert RiskLevel.CRITICAL.rank == 3
        assert RiskLevel.LOW.rank == 0


class TestSecurity:
    def test_permissions(self) -> None:
        engine = build_devops_engine()
        security = engine.security
        assert security.can("ana", "deploy", granted=["deploy"]) is True
        security.grant("ana", "*")
        assert security.can("ana", "anything") is True

    def test_approval_policy(self) -> None:
        engine = build_devops_engine()
        security = engine.security
        assert security.approve("admin") is True
        assert security.approve("visitor") is False

    def test_requires_approval(self) -> None:
        security = build_devops_engine().security
        assert security.requires_approval(100000.0) is True
        assert security.requires_approval(10.0) is False

    def test_destructive_authority(self) -> None:
        security = build_devops_engine().security
        assert security.requires_authority("terminate") is True
        assert security.requires_authority("deploy") is False

    def test_sanitize(self) -> None:
        security = build_devops_engine().security
        assert security.is_safe("hello") is True
        assert security.is_safe("<script>alert(1)</script>") is False
        assert security.sanitize("<script>alert(1)</script>") == ""


class TestRegistry:
    def test_server_crud(self) -> None:
        registry = DevopsRegistry()
        server = Server(server_id="s1", name="app")
        registry.register_server(server)
        assert registry.get_server("s1") is server
        assert registry.list_servers() == [server]
        assert registry.remove_server("s1") is True
        assert registry.get_server("s1") is None

    def test_pipelines_and_builds(self) -> None:
        registry = DevopsRegistry()
        from devops_engine.devops_models import Build, Pipeline
        pipeline = Pipeline(pipeline_id="p1", name="ci")
        build = Build(build_id="b1", pipeline_id="p1")
        registry.register_pipeline(pipeline)
        registry.register_build(build)
        assert registry.get_pipeline("p1") is pipeline
        assert registry.list_builds() == [build]

    def test_incidents_and_costs(self) -> None:
        registry = DevopsRegistry()
        from devops_engine.devops_models import Incident, CostRecord
        incident = Incident(incident_id="i1", title="outage")
        cost = CostRecord(cost_id="c1", resource="db")
        registry.register_incident(incident)
        registry.register_cost(cost)
        assert registry.list_incidents() == [incident]
        assert registry.list_costs() == [cost]

    def test_stats(self) -> None:
        registry = DevopsRegistry()
        registry.register_server(Server(server_id="s1", name="a"))
        registry.register_container(
            Container(container_id="c1", name="b"))
        stats = registry.stats()
        assert stats["servers"] == 1
        assert stats["containers"] == 1
        assert stats["deployments"] == 0


class TestManagerAndEngine:
    def test_server_lifecycle(self, engine: DevopsEngine) -> None:
        server = engine.provision_server("api", cpu=4, memory_gb=16)
        assert server.cpu == 4
        assert server.memory_gb == 16
        assert server.status == ResourceStatus.RUNNING
        assert engine.terminate_server(server.server_id, "admin") is True
        assert server.status == ResourceStatus.TERMINATED

    def test_terminate_denied_for_low_role(self, engine: DevopsEngine) -> None:
        server = engine.provision_server("api")
        assert engine.terminate_server(server.server_id, "guest") is False
        assert server.status == ResourceStatus.RUNNING

    def test_deploy_flow(self, engine: DevopsEngine) -> None:
        deployment = engine.deploy("erp", "registry.local/erp:1.0",
                                   replicas=3)
        assert deployment.status == DeploymentStatus.COMPLETED
        assert deployment.desired == 3

    def test_pipeline_flow(self, engine: DevopsEngine) -> None:
        pipeline = engine.create_pipeline("ci", ["test", "build", "deploy"])
        assert engine.run_pipeline(pipeline.pipeline_id) is True
        assert pipeline.status == PipelineStatus.SUCCEEDED
        assert engine.metrics.count("devops.builds") == 1

    def test_health_and_log(self, engine: DevopsEngine) -> None:
        check = engine.check_health("api.internal")
        assert check.status == HealthStatus.HEALTHY
        entry = engine.collect_log("api", "request failed", "error")
        assert entry.level == "error"

    def test_backup_restore_flow(self, engine: DevopsEngine) -> None:
        backup = engine.start_backup("postgres")
        restore = engine.restore(backup.backup_id, target="postgres-new")
        assert restore.status == RestoreStatus.SUCCEEDED
        assert restore.target == "postgres-new"

    def test_incident_flow(self, engine: DevopsEngine) -> None:
        incident = engine.raise_incident("db down", Severity.CRITICAL)
        assert incident.status == IncidentStatus.OPEN
        assert engine.resolve_incident(incident.incident_id) is True
        assert incident.status == IncidentStatus.RESOLVED

    def test_cost_record(self, engine: DevopsEngine) -> None:
        cost = engine.record_cost("db", 150.50, period="2026-07")
        assert cost.amount == 150.50
        assert engine.registry.list_costs() == [cost]

    def test_attach_subsystem(self, engine: DevopsEngine) -> None:
        class FakeSubsystem:
            def ping(self) -> str:
                return "pong"

        fake = FakeSubsystem()
        engine.attach_subsystem("fake_engine", fake)
        assert engine.fake_engine.ping() == "pong"
        assert engine.manager.fake_engine.ping() == "pong"  # type: ignore[attr-defined]
        assert "fake_engine" in engine.stats()["subsystems"]

    def test_runtime_lifecycle(self, engine: DevopsEngine) -> None:
        assert engine.start() is True
        assert engine.runtime.is_running() is True
        assert engine.stop() is True
        assert engine.runtime.is_running() is False

    def test_factory_overrides(self) -> None:
        built = build_devops_engine({"region": "eu-west-1"})
        assert built.config.region == "eu-west-1"

    def test_stats(self, engine: DevopsEngine) -> None:
        engine.provision_server("a")
        stats = engine.stats()
        assert "manager" in stats
        assert stats["manager"]["registry"]["servers"] == 1


class TestContext:
    def test_snapshot(self, engine: DevopsEngine) -> None:
        snapshot = engine.context.snapshot()
        assert snapshot["environment"] == "production"
        assert snapshot["tenant"] == "default"


class TestInterfaces:
    def test_abstract_binding(self) -> None:
        from devops_engine.devops_interfaces import (CloudProviderAPI,
                                                     ContainerRuntime,
                                                     PipelineRunner)

        class FakeCloud(CloudProviderAPI):
            def provision(self, server: Server) -> bool:
                return True

            def terminate(self, server: Server) -> bool:
                return True

        assert issubclass(FakeCloud, CloudProviderAPI)
        assert issubclass(ContainerRuntime, object)
        assert PipelineRunner.__abstractmethods__
