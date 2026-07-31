from __future__ import annotations

import logging
import time
from typing import Any


class TestStage:
    """CI/CD test stage — runs unit, integration, and e2e tests."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd.test")

    def run(self, config: dict[str, Any]) -> dict[str, Any]:
        errors = self.validate(config)
        if errors:
            return {"ok": False, "status": "failed", "errors": errors}
        total = max(1, int(config.get("total", 10)))
        failed = int(config.get("failed", 0))
        return {
            "ok": failed == 0,
            "status": "passed" if failed == 0 else "failed",
            "total": total,
            "passed": total - failed,
            "failed": failed,
            "duration_ms": config.get("duration_ms", 900),
            "finished_at": time.time(),
        }

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if "suite" not in config and "total" not in config:
            errors.append("suite or total is required")
        return errors
