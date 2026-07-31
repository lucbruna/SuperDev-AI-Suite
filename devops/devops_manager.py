from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .devops_engine import DevOpsEngine


class DevOpsManager:
    """Manages DevOps lifecycle and subsystem coordination."""

    def __init__(self, engine: DevOpsEngine) -> None:
        self._log = logging.getLogger("superdev.devops.manager")
        self._engine = engine

    def create_environment(self, name: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        """Provision a new environment through the engine."""
        return self._engine.provision(name, **(config or {}))

    def deploy_service(self, service: str, environment: str, **kwargs: Any) -> dict[str, Any]:
        """Deploy a service through the engine (real DeploymentEngine)."""
        return self._engine.deploy(service, environment, **kwargs)

    def get_status(self, environment: str | None = None) -> dict[str, Any]:
        """Return the aggregated engine status."""
        return self._engine.status(environment)

    def list_environments(self) -> list[str]:
        """List known environment names."""
        return list(self._engine.status()["environments"])

    def list_services(self) -> list[dict[str, Any]]:
        """List registered services."""
        return [s.__dict__ for s in self._engine.services]
