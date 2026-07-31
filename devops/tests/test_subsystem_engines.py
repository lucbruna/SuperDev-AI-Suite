"""Tests for the implemented subsystem engines (docker/cloud/environments/terraform/cicd)."""

from __future__ import annotations

import pytest

from devops.cicd.cicd_engine import CICDEngine
from devops.cloud.cloud_engine import CloudEngine
from devops.devops_engine import DevOpsEngine
from devops.docker.docker_engine import DockerEngine
from devops.environments.environments_engine import EnvironmentsEngine
from devops.terraform.terraform_engine import TerraformEngine


class TestDockerEngine:
    def test_build_and_images(self) -> None:
        engine = DockerEngine()
        result = engine.build("./app", "app:v1")
        assert result["status"] == "completed"
        assert result["tag"] == "app:v1"
        assert any(i.get("tag") == "app:v1" for i in engine.list_images())
        assert engine.status()["images"] == 1

    def test_run_stop_inspect(self) -> None:
        engine = DockerEngine()
        engine.build("./app", "app:v1")
        container = engine.run("app:v1", name="web", ports=[8080])
        assert container["status"] == "running"
        assert engine.stop(container["container_id"]) is True
        assert engine.inspect(container["container_id"])["status"] == "stopped"
        assert len(engine.list_containers()) == 1

    def test_image_manager_ops(self) -> None:
        engine = DockerEngine()
        engine.images.pull("nginx:latest")
        assert engine.images.tag("nginx:latest", "stable") is True
        assert engine.images.remove("nginx:latest") is True
        assert engine.images.remove("nginx:latest") is False


class TestCloudEngine:
    def test_provision_destroy_list(self) -> None:
        engine = CloudEngine()
        engine.providers.register("aws", object())
        created = engine.provision("aws", "compute", "api-node", instances=2)
        assert created["status"] == "running"
        assert engine.get_status("aws", created["resource_id"])["name"] == "api-node"
        assert len(engine.list_resources("aws")) == 1
        assert engine.destroy("aws", created["resource_id"]) is True

    def test_provision_unknown_provider(self) -> None:
        engine = CloudEngine()
        with pytest.raises(ValueError, match="unknown cloud provider"):
            engine.provision("nope", "compute", "x")

    def test_estimate_cost(self) -> None:
        engine = CloudEngine()
        cost = engine.estimate_cost("aws", {"resource_type": "compute", "instances": 2})
        assert cost["monthly_estimate"] > 0
        assert cost["instances"] == 2

    def test_resource_manager_tag(self) -> None:
        engine = CloudEngine()
        engine.providers.register("aws", object())
        created = engine.provision("aws", "storage", "bucket")
        assert engine.resources.tag("aws", created["resource_id"], {"env": "prod"}) is True


class TestEnvironmentsEngine:
    def test_lifecycle(self) -> None:
        engine = EnvironmentsEngine()
        engine.create("staging", "staging")
        assert engine.activate("staging") is True
        assert engine.get("staging")["active"] is True
        engine.set_variable("staging", "API_KEY", "abc")
        assert engine.variables("staging")["API_KEY"] == "abc"
        assert engine.deactivate("staging") is True
        assert engine.destroy("staging") is True
        assert engine.destroy("staging") is False

    def test_promote(self) -> None:
        engine = EnvironmentsEngine()
        engine.create("staging", "staging", variables={"DB_URL": "x"})
        promoted = engine.promote("staging", "production")
        assert promoted["status"] == "promoted"
        assert engine.variables("production")["DB_URL"] == "x"

    def test_duplicate_create(self) -> None:
        engine = EnvironmentsEngine()
        engine.create("qa", "staging")
        with pytest.raises(ValueError):
            engine.create("qa", "staging")


class TestTerraformEngine:
    def test_apply_destroy_state(self) -> None:
        engine = TerraformEngine()
        engine.init("./infra")
        plan = engine.plan("./infra", names=["api", "db"])
        assert plan["status"] == "planned"
        applied = engine.apply("./infra", resources=plan["resources"])
        assert applied["status"] == "applied"
        assert set(engine.state_list("./infra")) == set(plan["resources"])
        assert engine.state_rm("./infra", plan["resources"][0]) is True
        assert engine.destroy("./infra")["status"] == "destroyed"

    def test_validate_and_fmt(self) -> None:
        engine = TerraformEngine()
        assert engine.validate("./infra")["valid"] is True
        assert engine.fmt("./infra")["formatted"] is True


class TestCICDEngine:
    def test_pipeline_pass(self) -> None:
        engine = CICDEngine()
        engine.builder.create(
            "release",
            stages=[
                {"name": "build", "type": "build", "config": {"project": "billing"}},
                {"name": "test", "type": "test", "config": {"total": 10, "failed": 0}},
                {"name": "security", "type": "security", "config": {"project": "billing"}},
            ],
        )
        run = engine.run_pipeline("release")
        assert run["status"] == "passed"
        assert [s["type"] for s in run["stages"]] == ["build", "test", "security"]
        status = engine.get_status(run["pipeline_id"])
        assert status["last_status"] == "passed"

    def test_pipeline_fails_on_failed_stage(self) -> None:
        engine = CICDEngine()
        engine.builder.create(
            "broken",
            stages=[
                {"name": "build", "type": "build", "config": {"project": "x"}},
                {"name": "test", "type": "test", "config": {"total": 10, "failed": 3}},
            ],
        )
        run = engine.run_pipeline("broken")
        assert run["status"] == "failed"
        assert run["stages"][1]["status"] == "failed"

    def test_approval_stage_manual(self) -> None:
        engine = CICDEngine()
        engine.builder.create(
            "gated",
            stages=[
                {"name": "approval", "type": "approval", "config": {"auto_approve": False}},
                {"name": "deploy", "type": "deploy", "config": {"service": "api"}},
            ],
        )
        run = engine.run_pipeline("gated")
        assert run["status"] == "failed"  # approval pending blocks the pipeline
        assert run["stages"][0]["status"] == "pending"

    def test_unknown_pipeline(self) -> None:
        engine = CICDEngine()
        with pytest.raises(KeyError):
            engine.run_pipeline("missing")


class TestDevOpsEngineDelegation:
    def test_build_delegates_to_docker(self) -> None:
        engine = DevOpsEngine()
        record = engine.build("billing", version="v1", path="./billing")
        assert record["status"] == "built"
        assert record["image"] == "billing:v1"
        assert engine.docker.status()["images"] == 1

    def test_build_with_pipeline(self) -> None:
        engine = DevOpsEngine()
        record = engine.build("billing", version="v1", pipeline="release")
        assert record["pipeline_run"]["status"] == "passed"

    def test_provision_delegates_to_subsystems(self) -> None:
        engine = DevOpsEngine()
        result = engine.provision("staging", resource_types=["compute", "database"])
        assert result["status"] == "provisioned"
        assert len(result["resources"]) == 2
        assert len(result["cloud_resources"]) == 2
        assert engine.environments.get("staging")["name"] == "staging"

    def test_destroy_delegates_to_subsystems(self) -> None:
        engine = DevOpsEngine()
        engine.provision("staging")
        result = engine.destroy("staging")
        assert result["destroyed"] is True
        with pytest.raises(KeyError):
            engine.environments.get("staging")
        assert "staging" not in engine.status()["environments"]
