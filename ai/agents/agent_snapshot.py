from __future__ import annotations

import time
from typing import Any


class AgentSnapshot:
    """Snapshot management for agent state."""

    def __init__(self) -> None:
        self._snapshots: dict[str, dict[str, Any]] = {}

    def take(self, agent_id: str, state: dict[str, Any]) -> None:
        self._snapshots[agent_id] = {
            "state": state,
            "timestamp": time.time(),
        }

    def restore(self, agent_id: str) -> dict[str, Any] | None:
        snap = self._snapshots.get(agent_id)
        return snap["state"] if snap else None

    def list_snapshots(self) -> list[str]:
        return list(self._snapshots.keys())

    def remove(self, agent_id: str) -> bool:
        return self._snapshots.pop(agent_id, None) is not None

    def clear(self) -> None:
        self._snapshots.clear()
