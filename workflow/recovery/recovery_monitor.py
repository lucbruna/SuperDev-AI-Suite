from __future__ import annotations

import logging
import time
from typing import Any

from .recovery_models import RecoveryPlan


class RecoveryMonitor:
    """Monitors recovery operations and status."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._log = logging.getLogger("superdev.workflow.recovery.monitor")

    def record(self, plan: RecoveryPlan) -> None:
        self._records.append({
            "plan_id": plan.id,
            "status": plan.status.value,
            "timestamp": time.time(),
        })

    def summary(self) -> dict[str, Any]:
        total = len(self._records)
        succeeded = sum(1 for r in self._records if r["status"] == "completed")
        return {"total": total, "succeeded": succeeded, "failed": total - succeeded}
