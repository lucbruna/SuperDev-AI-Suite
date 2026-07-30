from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .planner_checkpoint import PlannerCheckpoint


class PlannerRecovery:
    """Recovery system for failed plan executions."""

    def __init__(self):
        self.checkpointer = PlannerCheckpoint()
        self._recovery_log: list[dict[str, Any]] = []

    def recover(self, plan_id: str) -> dict[str, Any] | None:
        checkpoints = self.checkpointer.list_checkpoints(plan_id)
        if not checkpoints:
            return None
        latest = checkpoints[-1]
        state = self.checkpointer.load(latest["checkpoint_id"] if "checkpoint_id" in latest else "")
        self._recovery_log.append({
            "plan_id": plan_id,
            "action": "recovered",
            "from_checkpoint": latest.get("timestamp"),
            "timestamp": datetime.now(UTC).isoformat(),
        })
        return state

    def get_recovery_history(self, plan_id: str | None = None) -> list[dict[str, Any]]:
        if plan_id:
            return [r for r in self._recovery_log if r["plan_id"] == plan_id]
        return list(self._recovery_log)
