from __future__ import annotations

import logging
from typing import Any

from .recovery_models import RecoveryPlan


class RecoveryManager:
    """Manages recovery plan lifecycle."""

    def __init__(self) -> None:
        self._plans: dict[str, RecoveryPlan] = {}
        self._log = logging.getLogger("superdev.workflow.recovery.manager")

    def register(self, plan: RecoveryPlan) -> None:
        self._plans[plan.id] = plan
        self._log.info("Registered recovery plan %s", plan.id)

    def get(self, plan_id: str) -> RecoveryPlan | None:
        return self._plans.get(plan_id)

    def list_all(self) -> list[RecoveryPlan]:
        return list(self._plans.values())
