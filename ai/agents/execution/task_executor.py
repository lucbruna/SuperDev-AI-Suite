"""Individual task execution handler."""
from __future__ import annotations

import time
import uuid
from typing import Any


class TaskExecutor:
    """Executes individual tasks and tracks their state."""

    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}

    async def execute(self, task_spec: dict[str, Any]) -> dict[str, Any]:
        task_id = task_spec.get("id", str(uuid.uuid4()))
        self._tasks[task_id] = {
            "id": task_id,
            "status": "running",
            "spec": task_spec,
            "started_at": time.time(),
            "result": None,
        }
        task_type = task_spec.get("type", "generic")
        payload = task_spec.get("payload", {})
        result: dict[str, Any] = {
            "task_id": task_id,
            "type": task_type,
            "output": f"Executed {task_type} task with {len(payload)} payload items",
            "completed_at": time.time(),
        }
        self._tasks[task_id].update({
            "status": "completed",
            "result": result,
            "completed_at": time.time(),
        })
        return result

    def cancel(self, task_id: str) -> bool:
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if task["status"] == "running":
                task["status"] = "cancelled"
                return True
        return False

    def get_status(self, task_id: str) -> dict[str, Any] | None:
        task = self._tasks.get(task_id)
        if task:
            return {
                "id": task["id"],
                "status": task["status"],
                "started_at": task["started_at"],
                "completed_at": task.get("completed_at"),
            }
        return None

    def get_all_tasks(self) -> dict[str, dict[str, Any]]:
        return {
            tid: {"id": t["id"], "status": t["status"]}
            for tid, t in self._tasks.items()
        }
