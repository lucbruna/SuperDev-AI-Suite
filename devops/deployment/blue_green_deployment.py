from __future__ import annotations

import logging
import time
from typing import Any

from ..devops_interfaces import IDeploymentStrategy


class BlueGreenDeployment(IDeploymentStrategy):
    """Blue-green deployment strategy — deploys to standby then switches traffic."""

    name = "blue_green"

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.blue_green")
        self._state: dict[str, dict[str, Any]] = {}

    def deploy(self, service: str, environment: str, config: dict[str, Any]) -> dict[str, Any]:
        deployment_id = config.get("deployment_id", "")
        self._state[deployment_id] = {
            "deployment_id": deployment_id,
            "service": service,
            "environment": environment,
            "status": "prepared",
            "active": "blue",
            "standby": "green",
            "deployed_at": time.time(),
        }
        self._log.info("blue-green deploy %s (green prepared)", deployment_id)
        return {
            "ok": True,
            "status": "prepared",
            "deployment_id": deployment_id,
            "service": service,
            "environment": environment,
            "active": "blue",
            "standby": "green",
        }

    def switch(self, deployment_id: str) -> dict[str, Any]:
        """Switch traffic to the standby environment (green becomes active)."""
        state = self._state.get(deployment_id)
        if state is None:
            return {"ok": False, "status": "failed", "error": "deployment not found"}
        state["status"] = "healthy"
        state["active"], state["standby"] = state["standby"], state["active"]
        self._log.info("blue-green switch %s → active=%s", deployment_id, state["active"])
        return {
            "ok": True,
            "status": "healthy",
            "deployment_id": deployment_id,
            "active": state["active"],
            "standby": state["standby"],
        }

    def rollback(self, deployment_id: str) -> dict[str, Any]:
        state = self._state.get(deployment_id)
        if state is None:
            return {"ok": False, "status": "failed", "error": "deployment not found"}
        state["status"] = "rolled_back"
        state["active"], state["standby"] = "blue", "green"
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
