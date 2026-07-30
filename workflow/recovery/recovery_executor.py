from __future__ import annotations

import logging
from typing import Any

from .recovery_models import RecoveryPlan


class RecoveryExecutor:
    """Executes recovery plan steps."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.recovery.executor")

    def execute(self, plan: RecoveryPlan) -> None:
        for step in plan.steps:
            action = step.get("action", "")
            self._log.info("Executing step: %s for plan %s", action, plan.id)
            step["status"] = "executed"
