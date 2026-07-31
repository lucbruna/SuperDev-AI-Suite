"""Tests for the JSON disk persistence of builds/environments/deployments."""

from __future__ import annotations

from pathlib import Path

import pytest

from devops.deployment.deployment_engine import DeploymentEngine
from devops.devops_engine import DevOpsEngine


class TestDeploymentEnginePersistence:
    def test_deploy_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "deploy-state"
        first = DeploymentEngine(store_path=store)
        record = first.deploy("api", "v1.2.0", strategy="canary")
        first.advance(record["deployment_id"])

        second = DeploymentEngine(store_path=store)
        assert second.status(record["deployment_id"])["status"] == "canary"
        assert second.list("api")[0]["version"] == "v1.2.0"
        assert (store / "deployments.json").exists()

    def test_rollback_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "deploy-state"
        first = DeploymentEngine(store_path=store)
        record = first.deploy("api", "v1")
        first.rollback(record["deployment_id"])

        second = DeploymentEngine(store_path=store)
        assert second.status(record["deployment_id"])["status"] == "rolled_back"

    def test_history_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "deploy-state"
        first = DeploymentEngine(store_path=store)
        record = first.deploy("api", "v1")
        first.rollback(record["deployment_id"])

        second = DeploymentEngine(store_path=store)
        entries = second.history("api")
        assert len(entries) == 2
        assert entries[0]["status"] == "healthy"
        assert entries[1]["status"] == "rolled_back"
        assert (store / "history.json").exists()

    def test_without_store_is_volatile(self, tmp_path: Path) -> None:
        store = tmp_path / "deploy-state"
        first = DeploymentEngine(store_path=store)
        record = first.deploy("api", "v1")

        fresh = DeploymentEngine(store_path=None)
        with pytest.raises(KeyError):
            fresh.status(record["deployment_id"])

    def test_corrupt_store_is_tolerated(self, tmp_path: Path) -> None:
        store = tmp_path / "deploy-state"
        store.mkdir()
        (store / "deployments.json").write_text("{ not valid json", encoding="utf-8")
        engine = DeploymentEngine(store_path=store)
        assert engine.list() == []
        # Still functional after a corrupt load.
        record = engine.deploy("api", "v1")
        assert record["status"] == "healthy"

    def test_strategy_state_survives_reload(self, tmp_path: Path) -> None:
        """Canary traffic step is restored so advance() keeps working after reload."""
        store = tmp_path / "deploy-state"
        first = DeploymentEngine(store_path=store)
        record = first.deploy("api", "v1", strategy="canary")
        first.advance(record["deployment_id"])  # step 1, traffic 0.25

        second = DeploymentEngine(store_path=store)
        assert second.status(record["deployment_id"])["strategy_status"]["traffic"] == pytest.approx(0.25)
        advanced = second.advance(record["deployment_id"])
        assert advanced["strategy_status"]["traffic"] == pytest.approx(0.5)


class TestDevOpsEnginePersistence:
    def test_builds_and_environments_survive_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "devops-state"
        first = DevOpsEngine(store_path=store)
        first.build("billing", version="v1.2.0")
        first.provision("staging", resource_types=["compute", "database"])

        second = DevOpsEngine(store_path=store)
        status = second.status()
        assert status["build_count"] == 1
        assert status["builds"][0]["service"] == "billing"
        assert status["environment_count"] == 1
        assert "staging" in status["environments"]
        assert (store / "builds.json").exists()
        assert (store / "environments.json").exists()

    def test_destroy_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "devops-state"
        first = DevOpsEngine(store_path=store)
        first.provision("staging")
        first.destroy("staging")

        second = DevOpsEngine(store_path=store)
        assert second.status()["environment_count"] == 0

    def test_deploy_through_engine_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "devops-state"
        first = DevOpsEngine(store_path=store)
        record = first.deploy("api", "staging", version="v1")
        first.rollback(record["deployment_id"])

        second = DevOpsEngine(store_path=store)
        assert second.deployment.status(record["deployment_id"])["status"] == "rolled_back"

    def test_save_state_and_reload_state(self, tmp_path: Path) -> None:
        store = tmp_path / "devops-state"
        engine = DevOpsEngine(store_path=store)
        engine.build("billing", version="v1")
        engine.provision("qa")
        engine.deploy("billing", "qa", version="v1")
        engine.save_state()

        # A fresh engine sees the persisted state.
        reloaded = DevOpsEngine(store_path=store)
        assert reloaded.status()["build_count"] == 1
        assert reloaded.status()["environment_count"] == 1
        assert reloaded.deployment.list() != []

    def test_corrupt_store_is_tolerated(self, tmp_path: Path) -> None:
        store = tmp_path / "devops-state"
        store.mkdir()
        (store / "builds.json").write_text("[broken", encoding="utf-8")
        engine = DevOpsEngine(store_path=store)
        assert engine.status()["build_count"] == 0
        engine.build("api", version="v1")
        assert engine.status()["build_count"] == 1

    def test_registry_restored_from_store(self, tmp_path: Path) -> None:
        store = tmp_path / "devops-state"
        first = DevOpsEngine(store_path=store)
        first.build("billing", version="v1", service_type="api")
        first.provision("staging", resource_types=["compute"])

        second = DevOpsEngine(store_path=store)
        assert second.status()["services"] == ["billing"]
        assert any(s.name == "billing" for s in second.services)
        # Environment resources are re-registered so destroy() can clean up.
        result = second.destroy("staging")
        assert result["destroyed"] is True
        assert second.status()["environment_count"] == 0
