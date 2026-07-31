from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class DeploymentsEngine:
    """Renders the deployments page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.deployments")
        self._context = context or FrontendContext()
        self._deployments: dict[str, dict[str, Any]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "deployments",
            "count": len(self._deployments),
            "deployments": self.list(),
        }

    def list(self) -> list[dict[str, Any]]:
        return [
            {"deployment_id": deployment_id, **deployment}
            for deployment_id, deployment in self._deployments.items()
        ]

    def deploy(self, project_id: str, environment: str = "production") -> str:
        deployment_id = f"deploy-{len(self._deployments) + 1}"
        self._deployments[deployment_id] = {
            "project_id": project_id,
            "environment": environment,
            "status": "deploying",
            "started_at": time.time(),
        }
        return deployment_id

    def status(self, deployment_id: str) -> dict[str, Any]:
        deployment = self._deployments.get(deployment_id)
        if deployment is None:
            raise KeyError(f"unknown deployment: {deployment_id}")
        return {"deployment_id": deployment_id, **deployment}

    def rollback(self, deployment_id: str) -> bool:
        deployment = self._deployments.get(deployment_id)
        if deployment is None:
            return False
        deployment["status"] = "rolled_back"
        return True
