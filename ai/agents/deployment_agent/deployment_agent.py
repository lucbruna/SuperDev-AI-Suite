from __future__ import annotations

from typing import Any

from .blue_green import BlueGreen
from .canary import Canary
from .docker_builder import DockerBuilder
from .helm_generator import HelmGenerator
from .kubernetes_builder import KubernetesBuilder
from .release_manager import ReleaseManager
from .rollback import Rollback
from .terraform_generator import TerraformGenerator


class DeploymentEngine:
    """Central orchestrator for deployment workflows."""

    def __init__(self) -> None:
        self._docker = DockerBuilder()
        self._kubernetes = KubernetesBuilder()
        self._helm = HelmGenerator()
        self._terraform = TerraformGenerator()
        self._release = ReleaseManager()
        self._rollback = Rollback()
        self._blue_green = BlueGreen()
        self._canary = Canary()

    @property
    def docker(self) -> DockerBuilder:
        return self._docker

    @property
    def kubernetes(self) -> KubernetesBuilder:
        return self._kubernetes

    @property
    def helm(self) -> HelmGenerator:
        return self._helm

    @property
    def terraform(self) -> TerraformGenerator:
        return self._terraform

    @property
    def release(self) -> ReleaseManager:
        return self._release

    @property
    def rollback(self) -> Rollback:
        return self._rollback

    @property
    def blue_green(self) -> BlueGreen:
        return self._blue_green

    @property
    def canary(self) -> Canary:
        return self._canary

    def run_deployment(self, target: dict[str, Any]) -> dict[str, Any]:
        image = target.get("image", "app:latest")
        self._docker.set_base(image)
        return {"status": "deployed", "image": image}

    def get_status(self) -> dict[str, Any]:
        return {
            "docker_layers": self._docker.layer_count,
            "kubernetes_deployments": self._kubernetes.deployment_count,
            "helm_templates": self._helm.template_count,
            "terraform_resources": self._terraform.resource_count,
            "releases": self._release.release_count,
            "snapshots": self._rollback.snapshot_count,
            "blue_green_active": self._blue_green.get_active(),
            "canary_percentage": self._canary.get_config()["percentage"],
        }

    def to_dict(self) -> dict[str, Any]:
        return {"agent": "deployment_agent", "status": self.get_status()}
