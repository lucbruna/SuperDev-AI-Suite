"""Agent suspension and resumption management."""

from __future__ import annotations

import time
from typing import Any


class SuspensionManager:
    """Manages agent suspension and resumption."""

    def __init__(self) -> None:
        self._suspended: dict[str, dict[str, Any]] = {}
        self._suspension_count: int = 0

    def suspend(self, agent_id: str, reason: str = "", preserve_state: bool = True) -> dict[str, Any]:
        self._suspended[agent_id] = {
            "reason": reason,
            "preserve_state": preserve_state,
            "suspended_at": time.time(),
        }
        self._suspension_count += 1
        return {"agent_id": agent_id, "status": "suspended", "reason": reason}

    def resume(self, agent_id: str) -> dict[str, Any]:
        info = self._suspended.pop(agent_id, None)
        if info is None:
            return {"agent_id": agent_id, "status": "error", "error": "Not suspended"}
        return {"agent_id": agent_id, "status": "resumed", "was_suspended_at": info["suspended_at"]}

    def is_suspended(self, agent_id: str) -> bool:
        return agent_id in self._suspended

    def get_suspended_agents(self) -> list[str]:
        return list(self._suspended.keys())

    def get_suspension_info(self, agent_id: str) -> dict[str, Any] | None:
        return self._suspended.get(agent_id)

    def force_resume_all(self) -> list[str]:
        ids = list(self._suspended.keys())
        for aid in ids:
            del self._suspended[aid]
        return ids

    def snapshot(self) -> dict[str, Any]:
        return {
            "suspended": list(self._suspended.keys()),
            "total_suspensions": self._suspension_count,
        }
