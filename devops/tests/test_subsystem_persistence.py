"""Tests for the JSON disk persistence of the subsystem engines (docker/environments/terraform/cicd)."""

from __future__ import annotations

from pathlib import Path

import pytest

from devops.cicd.cicd_engine import CICDEngine
from devops.devops_engine import DevOpsEngine
from devops.docker.docker_engine import DockerEngine
from devops.environments.environments_engine import EnvironmentsEngine
from devops.terraform.terraform_engine import TerraformEngine


class TestDockerPersistence:
    def test_images_and_containers_survive_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "docker-state"
        first = DockerEngine(store_path=store)
        first.build("./app", "app:v1")
        first.images.pull("nginx:latest")
        container = first.run("app:v1", name="web")
        first.stop(container["container_id"])

        second = DockerEngine(store_path=store)
        assert any(i.get("tag") == "app:v1" for i in second.list_images())
        assert any(i.get("image") == "nginx:latest" for i in second.list_images())
        assert second.inspect(container["container_id"])["status"] == "stopped"
        assert len(second.list_containers()) == 1
        assert (store / "docker.json").exists()

    def test_manager_direct_mutations_persist(self, tmp_path: Path) -> None:
        store = tmp_path / "docker-state"
        first = DockerEngine(store_path=store)
        first.images.pull("redis:7")
        first.images.tag("redis:7", "stable")

        second = DockerEngine(store_path=store)
        assert any(i.get("tag") == "redis:stable" for i in second.list_images())

    def test_without_store_is_volatile(self, tmp_path: Path) -> None:
        first = DockerEngine(store_path=tmp_path / "s")
        first.build("./app", "app:v1")
        fresh = DockerEngine(store_path=None)
        assert fresh.list_images() == []

    def test_corrupt_store_is_tolerated(self, tmp_path: Path) -> None:
        store = tmp_path / "docker-state"
        store.mkdir()
        (store / "docker.json").write_text("{ broken", encoding="utf-8")
        engine = DockerEngine(store_path=store)
        assert engine.list_images() == []
        engine.build("./app", "ok:v1")
        assert any(i.get("tag") == "ok:v1" for i in engine.list_images())


class TestEnvironmentsPersistence:
    def test_lifecycle_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "env-state"
        first = EnvironmentsEngine(store_path=store)
        first.create("staging", "staging", variables={"API_KEY": "abc"})
        first.activate("staging")
        first.set_variable("staging", "DB_URL", "x")

        second = EnvironmentsEngine(store_path=store)
        assert second.get("staging")["active"] is True
        assert second.variables("staging")["API_KEY"] == "abc"
        assert second.variables("staging")["DB_URL"] == "x"
        assert (store / "environments_lifecycle.json").exists()

    def test_promote_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "env-state"
        first = EnvironmentsEngine(store_path=store)
        first.create("staging", "staging", variables={"DB_URL": "x"})
        first.promote("staging", "production")

        second = EnvironmentsEngine(store_path=store)
        assert second.variables("production")["DB_URL"] == "x"

    def test_destroy_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "env-state"
        first = EnvironmentsEngine(store_path=store)
        first.create("qa", "staging")
        first.destroy("qa")
        second = EnvironmentsEngine(store_path=store)
        with pytest.raises(KeyError):
            second.get("qa")

    def test_corrupt_store_is_tolerated(self, tmp_path: Path) -> None:
        store = tmp_path / "env-state"
        store.mkdir()
        (store / "environments_lifecycle.json").write_text("{ broken", encoding="utf-8")
        engine = EnvironmentsEngine(store_path=store)
        assert engine.list() == []
        engine.create("staging", "staging")
        assert engine.get("staging")["name"] == "staging"


class TestTerraformPersistence:
    def test_state_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "tf-state"
        first = TerraformEngine(store_path=store)
        first.init("./infra")
        plan = first.plan("./infra", names=["api", "db"])
        first.apply("./infra", resources=plan["resources"])
        first.state_rm("./infra", plan["resources"][0])

        second = TerraformEngine(store_path=store)
        assert set(second.state_list("./infra")) == {"resource.db"}
        assert (store / "terraform.json").exists()

    def test_destroy_survives_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "tf-state"
        first = TerraformEngine(store_path=store)
        plan = first.plan("./infra", names=["api"])
        first.apply("./infra", resources=plan["resources"])
        first.destroy("./infra")
        second = TerraformEngine(store_path=store)
        assert second.state_list("./infra") == []

    def test_corrupt_store_is_tolerated(self, tmp_path: Path) -> None:
        store = tmp_path / "tf-state"
        store.mkdir()
        (store / "terraform.json").write_text("not json", encoding="utf-8")
        engine = TerraformEngine(store_path=store)
        assert engine.state_list("./infra") == []
        engine.init("./infra")
        assert engine.state_list("./infra") == []


class TestCICDPersistence:
    def test_pipelines_and_runs_survive_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "cicd-state"
        first = CICDEngine(store_path=store)
        first.builder.create(
            "release",
            stages=[
                {"name": "build", "type": "build", "config": {"project": "api"}},
                {"name": "test", "type": "test", "config": {"total": 10, "failed": 0}},
            ],
        )
        run = first.run_pipeline("release")

        second = CICDEngine(store_path=store)
        pipelines = second.list_pipelines()
        assert pipelines[0]["name"] == "release"
        assert [s["name"] for s in pipelines[0]["stages"]] == ["build", "test"]
        status = second.get_status(run["pipeline_id"])
        assert status["last_status"] == "passed"
        assert (store / "cicd.json").exists()

    def test_corrupt_store_is_tolerated(self, tmp_path: Path) -> None:
        store = tmp_path / "cicd-state"
        store.mkdir()
        (store / "cicd.json").write_text("nope", encoding="utf-8")
        engine = CICDEngine(store_path=store)
        assert engine.list_pipelines() == []
        engine.builder.create("x", stages=[{"name": "build", "type": "build", "config": {}}])
        assert engine.list_pipelines()[0]["name"] == "x"


class TestDevOpsEngineSubsystemPersistence:
    def test_subsystems_survive_engine_reload(self, tmp_path: Path) -> None:
        store = tmp_path / "devops-state"
        first = DevOpsEngine(store_path=store)
        first.build("api", version="v1", pipeline="release")
        first.provision("staging", resource_types=["compute"])
        first.environments.set_variable("staging", "API_KEY", "abc")

        second = DevOpsEngine(store_path=store)
        # docker image built during engine.build survives
        assert any(i.get("tag") == "api:v1" for i in second.docker.list_images())
        # cicd pipeline + run created during engine.build survive
        assert second.cicd.list_pipelines() != []
        assert second.cicd.status()["runs"] == 1
        # environments lifecycle record created during engine.provision survives
        assert second.environments.variables("staging")["API_KEY"] == "abc"
        assert (store / "docker.json").exists()
        assert (store / "cicd.json").exists()
        assert (store / "environments_lifecycle.json").exists()

    def test_save_state_and_reload_state_delegate(self, tmp_path: Path) -> None:
        store = tmp_path / "devops-state"
        engine = DevOpsEngine(store_path=store)
        engine.build("api", version="v1")
        engine.provision("staging")
        engine.save_state()
        reloaded = DevOpsEngine(store_path=store)
        assert reloaded.docker.list_images() != []
        assert reloaded.environments.get("staging")["name"] == "staging"

    def test_engine_environments_file_is_not_clobbered(self, tmp_path: Path) -> None:
        """DevOpsEngine registry (environments.json) and lifecycle (environments_lifecycle.json) coexist."""
        store = tmp_path / "devops-state"
        first = DevOpsEngine(store_path=store)
        first.provision("staging")
        first.environments.create("qa", "staging")

        second = DevOpsEngine(store_path=store)
        assert "staging" in second.status()["environments"]
        assert second.environments.get("qa")["name"] == "qa"
        assert (store / "environments.json").exists()
        assert (store / "environments_lifecycle.json").exists()
