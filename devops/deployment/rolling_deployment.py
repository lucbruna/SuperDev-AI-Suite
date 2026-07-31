from __future__ import annotations

import logging
from typing import Any

from ..devops_interfaces import IDeploymentStrategy


class RollingDeployment(IDeploymentStrategy):
    """Rolling deployment strategy."""

    name = "rolling"

    def __init__(self, batch_size: int = 1, wait_seconds: int = 10) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.rolling")
        self.batch_size = batch_size
        self.wait_seconds = wait_seconds

    def deploy(self, service: str, environment: str, config: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def rollback(self, deployment_id: str) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self, deployment_id: str) -> bool:
        raise NotImplementedError

    def status(self, deployment_id: str) -> dict[str, Any]:
        raise NotImplementedError
