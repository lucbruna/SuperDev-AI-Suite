from __future__ import annotations

from ..blue_green import BlueGreen
from ..canary import Canary
from ..deployment_agent import DeploymentEngine
from ..docker_builder import DockerBuilder
from ..helm_generator import HelmGenerator
from ..kubernetes_builder import KubernetesBuilder
from ..release_manager import ReleaseManager
from ..rollback import Rollback
from ..terraform_generator import TerraformGenerator


class TestDockerBuilder:
    def test_set_base(self) -> None:
        db = DockerBuilder()
        db.set_base("node:18")
        assert db.to_dict()["base_image"] == "node:18"

    def test_add_layer(self) -> None:
        db = DockerBuilder()
        db.add_layer("COPY . /app")
        assert db.layer_count == 1

    def test_build(self) -> None:
        db = DockerBuilder()
        db.add_layer("WORKDIR /app")
        result = db.build()
        assert "FROM" in result

    def test_to_dict(self) -> None:
        db = DockerBuilder()
        d = db.to_dict()
        assert "base_image" in d


class TestKubernetesBuilder:
    def test_add_deployment(self) -> None:
        kb = KubernetesBuilder()
        kb.add_deployment("api", "api:v1", 3)
        assert kb.deployment_count == 1

    def test_get_deployment(self) -> None:
        kb = KubernetesBuilder()
        kb.add_deployment("api", "api:v1")
        assert kb.get_deployment("api") is not None

    def test_add_service(self) -> None:
        kb = KubernetesBuilder()
        kb.add_service("api", 80)
        assert kb.service_count == 1

    def test_generate(self) -> None:
        kb = KubernetesBuilder()
        kb.add_deployment("api", "api:v1")
        result = kb.generate()
        assert "Deployment" in result

    def test_to_dict(self) -> None:
        kb = KubernetesBuilder()
        kb.add_deployment("d", "i")
        d = kb.to_dict()
        assert "deployments" in d


class TestHelmGenerator:
    def test_add_template(self) -> None:
        hg = HelmGenerator()
        hg.add_template("deploy.yaml", "content")
        assert hg.template_count == 1

    def test_get_template(self) -> None:
        hg = HelmGenerator()
        hg.add_template("t.yaml", "data")
        assert hg.get_template("t.yaml") == "data"

    def test_set_value(self) -> None:
        hg = HelmGenerator()
        hg.set_value("replicas", 3)
        assert hg.to_dict()["values"]["replicas"] == 3

    def test_generate(self) -> None:
        hg = HelmGenerator()
        hg.set_value("image", "app")
        result = hg.generate()
        assert "Values" in result

    def test_to_dict(self) -> None:
        hg = HelmGenerator()
        hg.add_template("t", "c")
        d = hg.to_dict()
        assert "templates" in d


class TestTerraformGenerator:
    def test_add_provider(self) -> None:
        tg = TerraformGenerator()
        tg.add_provider("aws", {"region": "us-east-1"})
        assert tg.resource_count == 0

    def test_add_resource(self) -> None:
        tg = TerraformGenerator()
        tg.add_resource("aws_instance", "web", {"ami": "ami-123"})
        assert tg.resource_count == 1

    def test_get_resource(self) -> None:
        tg = TerraformGenerator()
        tg.add_resource("aws_instance", "web", {})
        assert tg.get_resource("aws_instance", "web") is not None

    def test_generate(self) -> None:
        tg = TerraformGenerator()
        tg.add_resource("aws_s3_bucket", "data", {"bucket": "my-bucket"})
        result = tg.generate()
        assert "aws_s3_bucket" in result

    def test_to_dict(self) -> None:
        tg = TerraformGenerator()
        tg.add_resource("r", "n", {})
        d = tg.to_dict()
        assert "resources" in d


class TestReleaseManager:
    def test_create_release(self) -> None:
        rm = ReleaseManager()
        rm.create_release("1.0.0", ["app.jar"])
        assert rm.release_count == 1

    def test_get_release(self) -> None:
        rm = ReleaseManager()
        rm.create_release("1.0.0", ["app.jar"])
        assert rm.get_release("1.0.0") is not None

    def test_promote(self) -> None:
        rm = ReleaseManager()
        rm.create_release("1.0.0", ["app.jar"])
        assert rm.promote("1.0.0", "production") is True

    def test_to_dict(self) -> None:
        rm = ReleaseManager()
        rm.create_release("1", ["a"])
        d = rm.to_dict()
        assert "releases" in d


class TestRollback:
    def test_create_snapshot(self) -> None:
        r = Rollback()
        r.create_snapshot("v1", {"image": "app:v1"})
        assert r.snapshot_count == 1

    def test_get_snapshot(self) -> None:
        r = Rollback()
        r.create_snapshot("v1", {"image": "app:v1"})
        assert r.get_snapshot("v1") is not None

    def test_rollback_to(self) -> None:
        r = Rollback()
        r.create_snapshot("v1", {"image": "app:v1"})
        result = r.rollback_to("v1")
        assert result["status"] == "rolled_back"

    def test_to_dict(self) -> None:
        r = Rollback()
        r.create_snapshot("s", {})
        d = r.to_dict()
        assert "snapshots" in d


class TestBlueGreen:
    def test_set_active(self) -> None:
        bg = BlueGreen()
        assert bg.set_active("green") is True

    def test_get_active(self) -> None:
        bg = BlueGreen()
        assert bg.get_active() == "blue"

    def test_deploy(self) -> None:
        bg = BlueGreen()
        bg.deploy("green", {"image": "v2"})
        assert bg.to_dict()["environments"]["green"] == {"image": "v2"}

    def test_switch(self) -> None:
        bg = BlueGreen()
        result = bg.switch()
        assert result["old"] == "blue"
        assert result["new"] == "green"

    def test_to_dict(self) -> None:
        bg = BlueGreen()
        d = bg.to_dict()
        assert "active" in d


class TestCanary:
    def test_configure(self) -> None:
        c = Canary()
        c.configure(10, 300)
        assert c.get_config()["percentage"] == 10

    def test_get_config(self) -> None:
        c = Canary()
        cfg = c.get_config()
        assert "percentage" in cfg

    def test_promote(self) -> None:
        c = Canary()
        c.configure(10, 300)
        c.promote()
        assert c.get_config()["percentage"] == 100

    def test_rollback(self) -> None:
        c = Canary()
        c.configure(10, 300)
        c.rollback()
        assert c.get_config()["percentage"] == 0

    def test_to_dict(self) -> None:
        c = Canary()
        c.configure(10, 300)
        d = c.to_dict()
        assert "config" in d


class TestDeploymentEngine:
    def test_engine_initializes(self) -> None:
        de = DeploymentEngine()
        assert de.docker is not None
        assert de.kubernetes is not None
        assert de.helm is not None
        assert de.terraform is not None
        assert de.release is not None
        assert de.rollback is not None
        assert de.blue_green is not None
        assert de.canary is not None

    def test_run_deployment(self) -> None:
        de = DeploymentEngine()
        result = de.run_deployment({"image": "app:latest"})
        assert result["status"] == "deployed"

    def test_get_status(self) -> None:
        de = DeploymentEngine()
        s = de.get_status()
        assert "docker_layers" in s

    def test_to_dict(self) -> None:
        de = DeploymentEngine()
        d = de.to_dict()
        assert d["agent"] == "deployment_agent"
