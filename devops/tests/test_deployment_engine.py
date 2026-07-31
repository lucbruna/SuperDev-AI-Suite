"""Tests for the real DeploymentEngine and its integration with the quality gate."""

from __future__ import annotations

import pytest

from devops.deployment import (
    BlueGreenDeployment,
    CanaryDeployment,
    DeploymentEngine,
    DeploymentHealth,
    DeploymentHistory,
    DeploymentSpec,
    DeploymentTarget,
    RollingDeployment,
)
from devops.devops_engine import DevOpsEngine


class TestDeploymentEngine:
    def test_deploy_default_rolling(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1.2.0")
        assert record["status"] == "healthy"
        assert record["service"] == "api"
        assert record["version"] == "v1.2.0"
        assert record["strategy"] == "rolling"
        assert record["deployment_id"].startswith("dep-")
        assert record["environment"] == "development"

    def test_deploy_with_canary_strategy(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v2.0.0", strategy="canary", environment="staging")
        assert record["status"] == "canary"
        assert record["strategy"] == "canary"
        assert record["environment"] == "staging"

    def test_deploy_unknown_strategy_raises(self) -> None:
        engine = DeploymentEngine()
        with pytest.raises(ValueError, match="unknown deployment strategy"):
            engine.deploy("api", "v1", strategy="stratos")

    def test_deploy_invalid_spec_raises(self) -> None:
        engine = DeploymentEngine()
        with pytest.raises(ValueError, match="invalid deployment spec"):
            engine.deploy("", "v1")

    def test_status_and_unknown(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1")
        status = engine.status(record["deployment_id"])
        assert status["deployment_id"] == record["deployment_id"]
        assert status["status"] == "healthy"
        assert "strategy_status" in status
        with pytest.raises(KeyError):
            engine.status("dep-unknown")

    def test_list_filter_by_service(self) -> None:
        engine = DeploymentEngine()
        engine.deploy("api", "v1")
        engine.deploy("web", "v1")
        records = engine.list("api")
        assert len(records) == 1
        assert records[0]["service"] == "api"
        assert len(engine.list()) == 2

    def test_rollback(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1")
        rolled = engine.rollback(record["deployment_id"])
        assert rolled["status"] == "rolled_back"
        assert engine.status(record["deployment_id"])["status"] == "rolled_back"

    def test_rollback_unknown_raises(self) -> None:
        engine = DeploymentEngine()
        with pytest.raises(KeyError):
            engine.rollback("dep-unknown")

    def test_cancel_in_flight(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1", strategy="canary")
        assert engine.cancel(record["deployment_id"]) is True
        assert engine.status(record["deployment_id"])["status"] == "cancelled"
        # Already terminal -> cannot cancel again.
        assert engine.cancel(record["deployment_id"]) is False

    def test_history(self) -> None:
        engine = DeploymentEngine()
        first = engine.deploy("api", "v1")
        engine.rollback(first["deployment_id"])
        entries = engine.history("api")
        assert len(entries) == 2
        assert entries[0]["status"] == "healthy"
        assert entries[1]["status"] == "rolled_back"

    def test_advance_canary_to_healthy(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1", strategy="canary")
        last = None
        for _ in range(6):
            last = engine.advance(record["deployment_id"])
            if last["status"] == "healthy":
                break
        assert last is not None
        assert last["status"] == "healthy"

    def test_advance_unsupported_strategy(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1", strategy="rolling")
        with pytest.raises(ValueError, match="does not support advance"):
            engine.advance(record["deployment_id"])

    def test_switch_blue_green(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1", strategy="blue_green")
        assert record["status"] == "prepared"
        switched = engine.switch(record["deployment_id"])
        assert switched["status"] == "healthy"

    def test_strategy_registration(self) -> None:
        engine = DeploymentEngine()
        engine.register_strategy("custom", RollingDeployment())
        assert "custom" in engine.list_strategies()
        assert engine.unregister_strategy("custom") is True
        assert engine.unregister_strategy("custom") is False

    def test_metrics_recorded(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1")
        engine.rollback(record["deployment_id"])
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("devops.deploys", 0) >= 1
        assert counters.get("devops.rollbacks", 0) >= 1


class TestStrategies:
    def test_rolling_validate(self) -> None:
        strat = RollingDeployment()
        result = strat.deploy("api", "prod", {"deployment_id": "dep-1", "instances": 3})
        assert result["ok"] is True
        assert strat.validate("dep-1") is True
        assert strat.status("dep-1")["status"] == "healthy"

    def test_canary_traffic_steps(self) -> None:
        strat = CanaryDeployment()
        strat.deploy("api", "prod", {"deployment_id": "dep-1"})
        state = strat.status("dep-1")
        assert state["traffic"] == pytest.approx(0.1)
        strat.advance("dep-1")
        assert strat.status("dep-1")["traffic"] == pytest.approx(0.25)
        assert strat.validate("dep-1") is False  # not yet healthy

    def test_blue_green_switch(self) -> None:
        strat = BlueGreenDeployment()
        strat.deploy("api", "prod", {"deployment_id": "dep-1"})
        assert strat.status("dep-1")["active"] == "blue"
        switched = strat.switch("dep-1")
        assert switched["status"] == "healthy"
        assert strat.status("dep-1")["active"] == "green"
        assert strat.validate("dep-1") is True


class TestDeploymentSupport:
    def test_spec_validate_and_to_dict(self) -> None:
        spec = DeploymentSpec("api", "v1").set("instances", 3)
        assert spec.validate() == []
        data = spec.to_dict()
        assert data["service"] == "api"
        assert data["spec"]["instances"] == 3
        assert DeploymentSpec("", "").validate() != []

    def test_target_capabilities_and_connect(self) -> None:
        target = DeploymentTarget("cluster-a", "kubernetes")
        assert target.connect() is True
        assert target.connected is True
        assert "canary" in target.capabilities()
        assert target.to_dict()["target_type"] == "kubernetes"
        assert target.disconnect() is True

    def test_history_diff_and_export(self) -> None:
        history = DeploymentHistory()
        history.record("dep-1", "api", "v1", status="healthy")
        history.record("dep-2", "api", "v2", status="healthy")
        diff = history.diff("dep-1", "dep-2")
        assert diff["version_changed"] is True
        assert len(history.list()) == 2
        assert len(history.list("api")) == 2
        assert '"dep-1"' in history.export()

    def test_health_engine(self) -> None:
        engine = DeploymentEngine()
        record = engine.deploy("api", "v1")
        health = DeploymentHealth(engine=engine)
        check = health.check(record["deployment_id"])
        assert check["healthy"] is True
        assert health.wait_ready(record["deployment_id"]) is True
        assert health.verify(record["deployment_id"], ["status"])["passed"] is True
        # auto rollback on unhealthy deployment
        engine.rollback(record["deployment_id"])
        rolled = health.auto_rollback(record["deployment_id"])
        assert rolled["rolled_back"] is True


class TestDeployWithQualityIntegration:
    def test_approved_gate_executes_real_deploy(self) -> None:
        engine = DevOpsEngine()
        result = engine.deploy_with_quality(
            "api",
            "staging",
            signals={"quality_score": 0.95, "coverage": 0.9, "tests_passed": True},
        )
        assert result["deployed"] is True
        assert result["status"] == "healthy"
        assert result["deployment_id"] is not None
        assert result["deployment"]["service"] == "api"
        # O deploy real ficou registrado no DeploymentEngine.
        assert len(engine.deployment.list()) == 1
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("devops.deploys", 0) >= 1

    def test_blocked_gate_does_not_deploy(self) -> None:
        engine = DevOpsEngine()
        result = engine.deploy_with_quality(
            "api",
            "production",
            signals={"quality_score": 0.4, "coverage": 0.2},
        )
        assert result["deployed"] is False
        assert result["status"] == "blocked"
        assert result["deployment_id"] is None
        # Nenhum deploy real foi executado.
        assert engine.deployment.list() == []
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("devops.deploys_blocked", 0) >= 1

    def test_deploy_rollback_status_through_engine(self) -> None:
        engine = DevOpsEngine()
        record = engine.deploy("api", "staging", version="v1")
        assert record["status"] == "healthy"
        status = engine.status("staging")
        assert status["count"] == 1
        rolled = engine.rollback(record["deployment_id"])
        assert rolled["status"] == "rolled_back"

    def test_manager_deploy_service(self) -> None:
        engine = DevOpsEngine()
        record = engine.manager.deploy_service("api", "production", version="v3")
        assert record["status"] == "healthy"
        assert record["version"] == "v3"
