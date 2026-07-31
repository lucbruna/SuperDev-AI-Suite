"""Core engine for deployment operations."""

from datetime import datetime
from typing import Any

from .deployer import Deployer
from .environment_manager import EnvironmentManager
from .models import Deployment, DeploymentStatus, Release
from .release_manager import ReleaseManager


class DeploymentEngine:
    """Central engine coordinating deployment operations."""

    def __init__(self):
        self.deployer = Deployer()
        self.release_manager = ReleaseManager()
        self.env_manager = EnvironmentManager()
        self._deployments: dict[str, Deployment] = {}
        self._releases: list[Release] = []

    def create_deployment(self, name: str, version: str, environment: str) -> Deployment:
        deployment = Deployment(name=name, version=version, environment=environment)
        self._deployments[deployment.deployment_id] = deployment
        return deployment

    def execute_deployment(self, deployment_id: str) -> bool:
        deployment = self._deployments.get(deployment_id)
        if not deployment:
            return False
        deployment.status = DeploymentStatus.IN_PROGRESS
        deployment.started_at = datetime.utcnow()
        success = self.deployer.deploy(deployment)
        deployment.status = DeploymentStatus.COMPLETED if success else DeploymentStatus.FAILED
        deployment.completed_at = datetime.utcnow()
        return success

    def create_release(self, version: str, name: str, description: str = "") -> Release:
        release = self.release_manager.create_release(version, name, description)
        self._releases.append(release)
        return release

    def get_deployment(self, deployment_id: str) -> Deployment | None:
        return self._deployments.get(deployment_id)

    def get_all_deployments(self) -> list[Deployment]:
        return list(self._deployments.values())

    def get_stats(self) -> dict[str, Any]:
        return {
            "deployments": len(self._deployments),
            "releases": len(self._releases),
            "environments": self.env_manager.count(),
        }
