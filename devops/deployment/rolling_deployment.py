from __future__ import annotations

import logging
import time
from typing import Any

from ..devops_interfaces import IDeploymentStrategy


class RollingDeployment(IDeploymentStrategy):
    """Rolling deployment strategy — updates instances in batches."""

    name = "rolling"

    def __init__(self, batch_size: int = 1, wait_seconds: int = 10) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.rolling")
        self.batch_size = batch_size
        self.wait_seconds = wait_seconds
        self._state: dict[str, dict[str, Any]] = {}

    def deploy(self, service: str, environment: str, config: dict[str, Any]) -> dict[str, Any]:
        deployment_id = config.get("deployment_id", "")
        instances = int(config.get("instances", 4))
        batches = max(1, (instances + self.batch_size - 1) // self.batch_size)
        self._state[deployment_id] = {
            "deployment_id": deployment_id,
            "service": service,
            "environment": environment,
            "status": "healthy",
            "instances": instances,
            "batches": batches,
            "deployed_at": time.time(),
        }
        self._log.info("rolling deploy %s (%d batches)", deployment_id, batches)
        return {
            "ok": True,
            "status": "healthy",
            "deployment_id": deployment_id,
            "service": service,
            "environment": environment,
            "instances": instances,
            "batches": batches,
        }

    def rollback(self, deployment_id: str) -> dict[str, Any]:
        state = self._state.get(deployment_id)
        if state is None:
            return {"ok": False, "status": "failed", "error": "deployment not found"}
        state["status"] = "rolled_back"
        state["rolled_back_at"] = time.time()
        return {"ok": True, "status": "rolled_back", "deployment_id": deployment_id}

    def validate(self, deployment_id: str) -> bool:
        state = self._state.get(deployment_id)
        return bool(state and state["status"] == "healthy")

    def status(self, deployment_id: str) -> dict[str, Any]:
        state = self._state.get(deployment_id)
        if state is None:
            return {"deployment_id": deployment_id, "status": "unknown"}
        return dict(state)

    def snapshot_state(self) -> dict[str, Any]:
        """Return a JSON-serializable snapshot of the strategy state."""
        return {k: dict(v) for k, v in self._state.items()}

    def restore_state(self, state: dict[str, Any]) -> None:
        """Restore strategy state from a persisted snapshot."""
        self._state = {k: dict(v) for k, v in state.items()}
