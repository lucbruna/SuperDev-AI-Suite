from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class AgentSnapshot:
    """Snapshot management for agent state."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, Dict[str, Any]] = {}

    def take(self, agent_id: str, state: Dict[str, Any]) -> None:
        self._snapshots[agent_id] = {
            "state": state,
            "timestamp": time.time(),
        }

    def restore(self, agent_id: str) -> Optional[Dict[str, Any]]:
        snap = self._snapshots.get(agent_id)
        return snap["state"] if snap else None

    def list_snapshots(self) -> List[str]:
        return list(self._snapshots.keys())

    def remove(self, agent_id: str) -> bool:
        return self._snapshots.pop(agent_id, None) is not None

    def clear(self) -> None:
        self._snapshots.clear()
