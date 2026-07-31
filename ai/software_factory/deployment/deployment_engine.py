"""Core engine for deployment operations."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Deployment, DeploymentStatus, Environment, Release
from .deployer import Deployer
from .release_manager import ReleaseManager
from .environment_manager import EnvironmentManager


class DeploymentEngine:
    """Central engine coordinating deployment operations."""

    def __init__(self):
        self.deployer = Deployer()
        self.release_manager = ReleaseManager()
        self.env_manager = EnvironmentManager()
        self._deployments: Dict[str, Deployment] = {}
        self._releases: List[Release] = []

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

    def get_deployment(self, deployment_id: str) -> Optional[Deployment]:
        return self._deployments.get(deployment_id)

    def get_all_deployments(self) -> List[Deployment]:
        return list(self._deployments.values())

    def get_stats(self) -> Dict[str, Any]:
        return {
            "deployments": len(self._deployments),
            "releases": len(self._releases),
            "environments": self.env_manager.count(),
        }
