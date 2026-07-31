"""Manager for deployment lifecycle and coordination."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Deployment, DeploymentStatus, DeploymentConfig, Environment


class DeploymentManager:
    """Manages deployment configurations and coordinates operations."""

    def __init__(self):
        self._deployments: Dict[str, Deployment] = {}
        self._configs: Dict[str, DeploymentConfig] = {}
        self._environments: Dict[str, Environment] = {}

    def add_deployment(self, deployment: Deployment) -> None:
        self._deployments[deployment.deployment_id] = deployment

    def get_deployment(self, deployment_id: str) -> Optional[Deployment]:
        return self._deployments.get(deployment_id)

    def add_config(self, config: DeploymentConfig) -> None:
        self._configs[config.config_id] = config

    def get_config(self, config_id: str) -> Optional[DeploymentConfig]:
        return self._configs.get(config_id)

    def add_environment(self, environment: Environment) -> None:
        self._environments[environment.env_id] = environment

    def get_environment(self, env_id: str) -> Optional[Environment]:
        return self._environments.get(env_id)

    def get_deployments_by_status(self, status: DeploymentStatus) -> List[Deployment]:
        return [d for d in self._deployments.values() if d.status == status]

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_deployments": len(self._deployments),
            "configs": len(self._configs),
            "environments": len(self._environments),
            "by_status": {
                s.value: sum(1 for d in self._deployments.values() if d.status == s)
                for s in DeploymentStatus
            },
        }
