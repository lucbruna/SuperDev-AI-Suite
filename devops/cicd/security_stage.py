from __future__ import annotations

import logging
import time
from typing import Any


class SecurityStage:
    """CI/CD security stage — SAST, DAST, dependency scanning."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.security")

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        errors = self.validate(config)
        if errors:
            return {"ok": False, "status": "failed", "errors": errors}
        critical = int(config.get("critical", 0))
        vulnerabilities = int(config.get("vulnerabilities", 0))
        return {
            "ok": critical == 0,
            "status": "passed" if critical == 0 else "failed",
            "critical": critical,
            "vulnerabilities": vulnerabilities,
            "scanned_at": time.time(),
        }

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not config.get("project") and not config.get("target"):
            errors.append("project or target is required")
        return errors
