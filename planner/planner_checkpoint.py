from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class PlannerCheckpoint:
    """Checkpoint system for plan execution."""

    def __init__(self):
        self._checkpoints: dict[str, dict[str, Any]] = {}

    def save(self, plan_id: str, state: dict[str, Any]) -> str:
        checkpoint_id = f"cp_{plan_id}_{int(datetime.now(UTC).timestamp())}"
        self._checkpoints[checkpoint_id] = {
            "plan_id": plan_id,
            "state": state,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return checkpoint_id

    def load(self, checkpoint_id: str) -> dict[str, Any] | None:
        cp = self._checkpoints.get(checkpoint_id)
        return cp.get("state") if cp else None

    def list_checkpoints(self, plan_id: str | None = None) -> list[dict[str, Any]]:
        if plan_id:
            return [cp for cp in self._checkpoints.values() if cp["plan_id"] == plan_id]
        return list(self._checkpoints.values())
