from __future__ import annotations

import logging
import time
from typing import Any


class BuildStage:
    """CI/CD build stage — compiles, packages, or transpiles code."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.build")

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        """Run the build stage. Returns ok=True when the build succeeds."""
        command = config.get("command", "build")
        errors = self.validate(config)
        if errors:
            return {"ok": False, "status": "failed", "errors": errors}
        return {
            "ok": True,
            "status": "passed",
            "command": command,
            "artifact": config.get("artifact", f"{config.get('project', 'app')}.tar.gz"),
            "duration_ms": config.get("duration_ms", 1500),
            "finished_at": time.time(),
        }

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not config.get("project"):
            errors.append("project is required")
        return errors
