"""Manager for deployment lifecycle and coordination."""

from typing import Any

from .models import Deployment, DeploymentConfig, DeploymentStatus, Environment


class DeploymentManager:
    """Manages deployment configurations and coordinates operations."""

    def __init__(self):
        self._deployments: dict[str, Deployment] = {}
        self._configs: dict[str, DeploymentConfig] = {}
        self._environments: dict[str, Environment] = {}

    def add_deployment(self, deployment: Deployment) -> None:
        self._deployments[deployment.deployment_id] = deployment

    def get_deployment(self, deployment_id: str) -> Deployment | None:
        return self._deployments.get(deployment_id)

    def add_config(self, config: DeploymentConfig) -> None:
        self._configs[config.config_id] = config

    def get_config(self, config_id: str) -> DeploymentConfig | None:
        return self._configs.get(config_id)

    def add_environment(self, environment: Environment) -> None:
        self._environments[environment.env_id] = environment

    def get_environment(self, env_id: str) -> Environment | None:
        return self._environments.get(env_id)

    def get_deployments_by_status(self, status: DeploymentStatus) -> list[Deployment]:
        return [d for d in self._deployments.values() if d.status == status]

    def get_statistics(self) -> dict[str, Any]:
        return {
            "total_deployments": len(self._deployments),
            "configs": len(self._configs),
            "environments": len(self._environments),
            "by_status": {
                s.value: sum(1 for d in self._deployments.values() if d.status == s) for s in DeploymentStatus
            },
        }
