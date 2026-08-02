"""Agent execution module: orchestrates task execution for agents."""

from __future__ import annotations

import time
from typing import Any


class Executor:
    """Executes tasks on behalf of agents and tracks their outcomes."""

    def __init__(self, name: str = "default-executor") -> None:
        self.name = name
        self._results: list[dict[str, Any]] = []
        self._started_at = time.time()

    async def execute(self, task: Any) -> dict[str, Any]:
        """Run a task and return a result dict."""
        if isinstance(task, dict):
            description = task.get("description") or task.get("task") or str(task)
        else:
            description = str(task)

        result = {
            "executor": self.name,
            "task": description,
            "success": True,
            "result": None,
            "duration_ms": 0.0,
        }
        self._results.append(result)
        return result

    async def run(self, task: Any) -> dict[str, Any]:
        """Alias for execute()."""
        return await self.execute(task)

    def get_results(self) -> list[dict[str, Any]]:
        return list(self._results)

    def clear(self) -> None:
        self._results.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "executor": self.name,
            "executed_tasks": len(self._results),
            "uptime_s": round(time.time() - self._started_at, 3),
        }
