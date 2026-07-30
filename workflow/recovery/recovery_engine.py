from __future__ import annotations

import logging
from typing import Any

from .recovery_models import RecoveryPlan, RecoveryStatus
from .recovery_planner import RecoveryPlanner
from .recovery_executor import RecoveryExecutor
from .recovery_audit import RecoveryAudit
from .recovery_monitor import RecoveryMonitor


class RecoveryEngine:
    """Central engine for recovery lifecycle."""

    def __init__(self) -> None:
        self._planner = RecoveryPlanner()
        self._executor = RecoveryExecutor()
        self._audit = RecoveryAudit()
        self._monitor = RecoveryMonitor()
        self._log = logging.getLogger("superdev.workflow.recovery")

    def recover(self, plan: RecoveryPlan) -> RecoveryPlan:
        plan.status = RecoveryStatus.IN_PROGRESS
        self._audit.log("started", plan.id)
        try:
            self._executor.execute(plan)
            plan.status = RecoveryStatus.COMPLETED
            self._audit.log("completed", plan.id)
        except Exception as exc:
            plan.status = RecoveryStatus.FAILED
            plan.error = str(exc)
            self._audit.log("failed", plan.id, {"error": str(exc)})
            self._log.exception("Recovery %s failed", plan.id)
        self._monitor.record(plan)
        return plan
