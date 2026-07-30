from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any


class PlannerSnapshot:
    """Snapshot management for planner state."""

    def __init__(self):
        self._snapshots: dict[str, dict[str, Any]] = {}

    def take(self, plan_id: str, data: dict[str, Any]) -> str:
        snapshot_id = f"snap_{plan_id}_{int(datetime.now(UTC).timestamp())}"
        self._snapshots[snapshot_id] = {
            "plan_id": plan_id,
            "data": data,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        return snapshot_id

    def restore(self, snapshot_id: str) -> dict[str, Any] | None:
        snap = self._snapshots.get(snapshot_id)
        return snap.get("data") if snap else None

    def to_json(self, snapshot_id: str) -> str | None:
        snap = self._snapshots.get(snapshot_id)
        return json.dumps(snap, indent=2, default=str) if snap else None
