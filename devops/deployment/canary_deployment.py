from __future__ import annotations

import logging
import time
from typing import Any

from ..devops_interfaces import IDeploymentStrategy


class CanaryDeployment(IDeploymentStrategy):
    """Canary deployment strategy with progressive traffic shifting."""

    name = "canary"

    def __init__(self, steps: list[float] | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.canary")
        self.steps = steps or [0.1, 0.25, 0.5, 1.0]
        self._state: dict[str, dict[str, Any]] = {}

    def deploy(self, service: str, environment: str, config: dict[str, Any]) -> dict[str, Any]:
        deployment_id = config.get("deployment_id", "")
        self._state[deployment_id] = {
            "deployment_id": deployment_id,
            "service": service,
            "environment": environment,
            "status": "canary",
            "step": 0,
            "traffic": self.steps[0],
            "total_steps": len(self.steps),
            "deployed_at": time.time(),
        }
        self._log.info("canary deploy %s (traffic %.0f%%)", deployment_id, self.steps[0] * 100)
        return {
            "ok": True,
            "status": "canary",
            "deployment_id": deployment_id,
            "service": service,
            "environment": environment,
            "step": 0,
            "traffic": self.steps[0],
            "total_steps": len(self.steps),
        }

    def advance(self, deployment_id: str) -> dict[str, Any]:
        """Shift more traffic to the canary. Returns status dict."""
        state = self._state.get(deployment_id)
        if state is None:
            return {"ok": False, "status": "failed", "error": "deployment not found"}
        if state["step"] + 1 >= len(self.steps):
            state["status"] = "healthy"
            state["traffic"] = 1.0
        else:
            state["step"] += 1
            state["traffic"] = self.steps[state["step"]]
        self._log.info("canary %s → step %d (traffic %.0f%%)", deployment_id, state["step"], state["traffic"] * 100)
        return {
            "ok": True,
            "status": state["status"],
            "deployment_id": deployment_id,
            "step": state["step"],
            "traffic": state["traffic"],
        }

    def rollback(self, deployment_id: str) -> dict[str, Any]:
        state = self._state.get(deployment_id)
        if state is None:
            return {"ok": False, "status": "failed", "error": "deployment not found"}
        state["status"] = "rolled_back"
        state["traffic"] = 0.0
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
