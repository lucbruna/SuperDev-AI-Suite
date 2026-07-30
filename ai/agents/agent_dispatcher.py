from __future__ import annotations

import time
from typing import Any, Dict


class AgentDispatcher:
    """Dispatches tasks to agents."""

    def __init__(self) -> None:
        self._dispatch_count: int = 0

    @property
    def dispatch_count(self) -> int:
        return self._dispatch_count

    def dispatch(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        self._dispatch_count += 1
        return {
            "dispatch_id": f"d{self._dispatch_count}",
            "agent_id": agent_id,
            "task": task,
            "timestamp": time.time(),
            "status": "dispatched",
        }

    def reset(self) -> None:
        self._dispatch_count = 0
