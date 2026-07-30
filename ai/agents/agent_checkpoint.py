from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class AgentCheckpoint:
    """Checkpoint for agent state persistence."""

    def __init__(self) -> None:
        self._checkpoints: Dict[str, Dict[str, Any]] = {}

    def save(self, agent_id: str, state: Dict[str, Any]) -> None:
        self._checkpoints[agent_id] = {
            "state": state,
            "timestamp": time.time(),
        }

    def load(self, agent_id: str) -> Optional[Dict[str, Any]]:
        cp = self._checkpoints.get(agent_id)
        return cp["state"] if cp else None

    def list_checkpoints(self) -> List[str]:
        return list(self._checkpoints.keys())

    def remove(self, agent_id: str) -> bool:
        return self._checkpoints.pop(agent_id, None) is not None

    def clear(self) -> None:
        self._checkpoints.clear()
