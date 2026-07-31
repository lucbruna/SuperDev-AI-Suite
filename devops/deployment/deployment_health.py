from __future__ import annotations

import logging
import time
from typing import Any


class DeploymentHealth:
    """Monitors deployment health and performs automated rollback."""

    def __init__(self, engine: Any = None) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.health")
        self._engine = engine

    def check(self, deployment_id: str) -> dict[str, Any]:
        """Health check for a deployment (uses the engine status when available)."""
        if self._engine is None:
            return {"deployment_id": deployment_id, "healthy": True, "error_rate": 0.0, "checks": []}
        try:
            record = self._engine.status(deployment_id)
        except KeyError:
            return {
                "deployment_id": deployment_id,
                "healthy": False,
                "error_rate": 1.0,
                "checks": [{"name": "exists", "ok": False}],
            }
        healthy = record.get("status") == "healthy"
        return {
            "deployment_id": deployment_id,
            "status": record.get("status"),
            "healthy": healthy,
            "error_rate": 0.0 if healthy else 1.0,
            "checks": [{"name": "status", "ok": healthy}],
        }

    def wait_ready(self, deployment_id: str, timeout: int = 300) -> bool:
        """Poll until the deployment is healthy or the timeout elapses."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.check(deployment_id)["healthy"]:
                return True
            time.sleep(0.01)
        return False

    def verify(self, deployment_id: str, checks: list[str]) -> dict[str, Any]:
        """Run a list of named checks against a deployment."""
        results = []
        passed = True
        for check in checks:
            ok = True
            if check == "status":
                ok = self.check(deployment_id)["healthy"]
            elif check == "version":
                ok = self._engine is not None
            results.append({"name": check, "ok": ok})
            passed = passed and ok
        return {
            "deployment_id": deployment_id,
            "passed": passed,
            "results": results,
        }

    def auto_rollback(self, deployment_id: str, threshold: float = 0.05) -> dict[str, Any]:
        """Roll back automatically when the error rate exceeds the threshold."""
        check = self.check(deployment_id)
        error_rate = float(check.get("error_rate", 0.0))
        if self._engine is None or check["healthy"] or error_rate < threshold:
            return {
                "deployment_id": deployment_id,
                "rolled_back": False,
                "reason": "healthy" if check["healthy"] else "below_threshold",
                "error_rate": error_rate,
            }
        record = self._engine.rollback(deployment_id)
        return {
            "deployment_id": deployment_id,
            "rolled_back": record.get("status") == "rolled_back",
            "status": record.get("status"),
            "error_rate": error_rate,
        }
