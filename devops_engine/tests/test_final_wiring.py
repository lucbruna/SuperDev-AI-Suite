"""Final wiring tests for the DevOps Engine (Volume 37, Fase 6)."""

from __future__ import annotations

import pytest

from devops_engine.devops_engine import DevopsEngine
from devops_engine.devops_events import DevopsEventType
from devops_engine.devops_factory import build_devops_engine
from devops_engine.devops_models import (DeploymentStatus, HealthStatus,
                                         ResourceStatus, RestoreStatus,
                                         ResourceType)


@pytest.fixture()
def engine() -> DevopsEngine:
    return build_devops_engine()


SUBSYSTEMS = ["cloud_engine", "container_engine", "kube_engine",
              "cicd_engine", "monitoring_engine", "logging_engine",
              "backup_engine", "recovery_engine", "scaling_engine",
              "cost_engine"]


class TestWiring:
    def test_all_subsystems_attached(self, engine: DevopsEngine) -> None:
        for name in SUBSYSTEMS:
            assert hasattr(engine, name)
            assert hasattr(engine.manager, name)

    def test_stats_lists_subsystems(self, engine: DevopsEngine) -> None:
        subsystems = engine.stats()["subsystems"]
        assert len(subsystems) == len(SUBSYSTEMS)
        for name in SUBSYSTEMS:
            assert name in subsystems

    def test_shared_events_bus(self, engine: DevopsEngine) -> None:
        seen: list[dict] = []
        engine.events.on(DevopsEventType.SCALED_UP, seen.append)
        policy = engine.scaling_engine.create_policy("c1")
        result = engine.scaling_engine.evaluate(policy.policy_id, 0.95)
        assert result["action"] == "up"
        assert len(seen) == 1

    def test_shared_metrics(self, engine: DevopsEngine) -> None:
        engine.cloud_engine.provision_server("api")
        assert engine.metrics.count("devops.cloud.servers") == 1


class TestEndToEnd:
    def test_full_scenario(self, engine: DevopsEngine) -> None:
        server = engine.cloud_engine.provision_server("api")
        assert server.status == ResourceStatus.RUNNING

        image = engine.container_engine.build("api", "1.0.0")
        container = engine.container_engine.run("api",
                                                f"{image.name}:{image.tag}")
        assert container.status.value == "running"

        cluster = engine.kube_engine.create_cluster("prod")
        deployment = engine.kube_engine.deploy(
            "api", "api:1.0.0", replicas=2, cluster_id=cluster.cluster_id)
        assert deployment.status == DeploymentStatus.COMPLETED

        pipeline = engine.cicd_engine.create_pipeline("ci",
                                                      ["test", "deploy"])
        assert engine.cicd_engine.run(pipeline.pipeline_id) is True

        engine.monitoring_engine.record_metric("cpu", 0.4)
        check = engine.monitoring_engine.check("api")
        assert check.status == HealthStatus.HEALTHY

        engine.logging_engine.collect("api", "all systems nominal")

        backup = engine.backup_engine.start_backup("postgres")
        assert engine.backup_engine.succeed_backup(backup.backup_id,
                                                   size_bytes=1024) is True
        restore = engine.recovery_engine.restore(backup.backup_id,
                                                 "postgres-new")
        assert restore.status == RestoreStatus.SUCCEEDED

        policy = engine.scaling_engine.create_policy(cluster.cluster_id,
                                                     min_replicas=1,
                                                     max_replicas=5)
        assert engine.scaling_engine.evaluate(policy.policy_id, 0.98)[
            "action"] == "up"

        cost = engine.cost_engine.record_cost("api", 42.0)
        assert cost.amount == 42.0
        resource = engine.cloud_engine.register_resource(
            "db", ResourceType.DATABASE, 0.5)
        resource.metadata["utilization"] = 0.2
        recommendations = engine.cost_engine.optimize([resource])
        assert len(recommendations) == 1
        assert recommendations[0].action == "downsize"

    def test_facade_manager_still_works(self, engine: DevopsEngine) -> None:
        server = engine.provision_server("core")
        assert server.status == ResourceStatus.RUNNING
        assert engine.terminate_server(server.server_id, "admin") is True
        assert server.status == ResourceStatus.TERMINATED

    def test_facade_observability(self, engine: DevopsEngine) -> None:
        check = engine.check_health("internal")
        assert check.status == HealthStatus.HEALTHY
        entry = engine.collect_log("api", "facade ok")
        assert entry.source == "api"

    def test_runtime_lifecycle(self, engine: DevopsEngine) -> None:
        assert engine.start() is True
        assert engine.runtime.is_running() is True
        assert engine.stop() is True
        assert engine.runtime.is_running() is False
