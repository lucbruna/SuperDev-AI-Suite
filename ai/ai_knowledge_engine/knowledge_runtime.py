"""Knowledge Runtime — Runtime environment for the knowledge platform."""

from datetime import datetime
from typing import Any


class KnowledgeRuntime:
    def __init__(self):
        self._running = False
        self._start_time: datetime | None = None
        self._tasks: dict[str, dict[str, Any]] = {}
        self._task_counter = 0

    def start(self) -> None:
        self._running = True
        self._start_time = datetime.now()

    def stop(self) -> None:
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def submit_task(self, name: str, task_type: str = "general", params: dict[str, Any] | None = None) -> str:
        self._task_counter += 1
        task_id = f"task_{self._task_counter}"
        self._tasks[task_id] = {
            "name": name,
            "type": task_type,
            "params": params or {},
            "status": "pending",
            "submitted_at": datetime.now().isoformat(),
        }
        return task_id

    def update_task(self, task_id: str, status: str, result: dict[str, Any] | None = None) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task["status"] = status
        if result:
            task["result"] = result
        return True

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        return self._tasks.get(task_id)

    def get_tasks(self, status: str | None = None) -> list[dict[str, Any]]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return tasks

    def get_uptime(self) -> float:
        if not self._start_time:
            return 0.0
        return (datetime.now() - self._start_time).total_seconds()

    def get_stats(self) -> dict[str, Any]:
        tasks = list(self._tasks.values())
        return {
            "running": self._running,
            "uptime_seconds": self.get_uptime(),
            "total_tasks": len(tasks),
            "pending": len([t for t in tasks if t["status"] == "pending"]),
            "completed": len([t for t in tasks if t["status"] == "completed"]),
            "failed": len([t for t in tasks if t["status"] == "failed"]),
        }
