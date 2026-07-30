from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class AgentExecutor:
    """Executes tasks assigned to agents."""

    def __init__(self) -> None:
        self._execution_count: int = 0
        self._history: List[Dict[str, Any]] = []
        self._max_history: int = 100

    @property
    def execution_count(self) -> int:
        return self._execution_count

    @property
    def history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def execute(self, agent_id: str, task: Dict[str, Any]) -> Dict[str, Any]:
        self._execution_count += 1
        result = {
            "execution_id": f"e{self._execution_count}",
            "agent_id": agent_id,
            "task": task,
            "timestamp": time.time(),
            "status": "completed",
        }
        self._history.append(result)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        return result

    def clear(self) -> None:
        self._execution_count = 0
        self._history.clear()
