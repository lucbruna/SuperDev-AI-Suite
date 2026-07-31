from __future__ import annotations

import time
from typing import Any


class AgentCheckpoint:
    """Checkpoint for agent state persistence."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, dict[str, Any]] = {}

    def save(self, agent_id: str, state: dict[str, Any]) -> None:
        self._checkpoints[agent_id] = {
            "state": state,
            "timestamp": time.time(),
        }

    def load(self, agent_id: str) -> dict[str, Any] | None:
        cp = self._checkpoints.get(agent_id)
        return cp["state"] if cp else None

    def list_checkpoints(self) -> list[str]:
        return list(self._checkpoints.keys())

    def remove(self, agent_id: str) -> bool:
        return self._checkpoints.pop(agent_id, None) is not None

    def clear(self) -> None:
        self._checkpoints.clear()
