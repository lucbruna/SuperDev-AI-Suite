from __future__ import annotations

import logging
from typing import Any

from .recovery_models import RecoveryPlan


class RecoveryPlanner:
    """Creates recovery plans for failed workflows."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.recovery.planner")

    def create_plan(self, target_type: str, target_id: str) -> RecoveryPlan:
        plan = RecoveryPlan(target_type=target_type, target_id=target_id)
        plan.steps.append({"action": "restore", "status": "planned"})
        self._log.info("Created recovery plan %s for %s/%s", plan.id, target_type, target_id)
        return plan
