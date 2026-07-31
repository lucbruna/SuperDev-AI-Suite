from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from .ai_exceptions import RuntimeError
from .ai_types import AgentStatus


class AIRuntime:
    """Execution environment for AI agents and tasks."""

    def __init__(self):
        self._tasks: dict[str, dict[str, Any]] = {}
        self._running: dict[str, asyncio.Task[Any]] = {}
        self._limits = {
            "max_concurrent": 10,
            "default_timeout": 300,
            "max_execution_time": 3600,
        }

    async def execute(
        self,
        task_id: str,
        coro: Any,
        *,
        timeout: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Any:
        """Execute a coroutine in the runtime."""
        if len(self._running) >= self._limits["max_concurrent"]:
            raise RuntimeError("Maximum concurrent tasks reached")

        task_timeout = timeout or self._limits["default_timeout"]
        self._tasks[task_id] = {
            "id": task_id,
            "status": "running",
            "started_at": datetime.now(UTC).isoformat(),
            "metadata": metadata or {},
        }

        try:
            task = asyncio.create_task(coro)
            self._running[task_id] = task
            result = await asyncio.wait_for(task, timeout=task_timeout)
            self._tasks[task_id]["status"] = "completed"
            self._tasks[task_id]["completed_at"] = datetime.now(UTC).isoformat()
            return result
        except TimeoutError:
            self._tasks[task_id]["status"] = "failed"
            self._tasks[task_id]["error"] = "timeout"
            raise RuntimeError(f"Task '{task_id}' timed out after {task_timeout}s", code="TIMEOUT")
        except Exception as e:
            self._tasks[task_id]["status"] = "failed"
            self._tasks[task_id]["error"] = str(e)
            raise
        finally:
            self._running.pop(task_id, None)

    async def cancel(self, task_id: str) -> None:
        """Cancel a running task."""
        task = self._running.get(task_id)
        if not task:
            raise RuntimeError(f"Task '{task_id}' not found or already completed")
        task.cancel()
        self._tasks[task_id]["status"] = "cancelled"
        self._tasks[task_id]["cancelled_at"] = datetime.now(UTC).isoformat()

    def cancel_all(self) -> None:
        """Cancel all running tasks."""
        for task_id in list(self._running.keys()):
            task = self._running[task_id]
            task.cancel()
            self._tasks[task_id]["status"] = "cancelled"
        self._running.clear()

    def get_status(self, task_id: str) -> AgentStatus | None:
        """Get the status of a task."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        return task["status"]

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Get task details."""
        return self._tasks.get(task_id)

    def list_tasks(self, status: str | None = None) -> list[dict[str, Any]]:
        """List all tasks, optionally filtered by status."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t["status"] == status]
        return tasks

    def get_statistics(self) -> dict[str, Any]:
        """Get runtime execution statistics."""
        total = len(self._tasks)
        running = sum(1 for t in self._tasks.values() if t["status"] == "running")
        completed = sum(1 for t in self._tasks.values() if t["status"] == "completed")
        failed = sum(1 for t in self._tasks.values() if t["status"] == "failed")
        cancelled = sum(1 for t in self._tasks.values() if t["status"] == "cancelled")

        return {
            "total_tasks": total,
            "running": running,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "concurrent_limit": self._limits["max_concurrent"],
            "active_tasks": len(self._running),
        }

    def set_limits(self, **kwargs: int) -> None:
        """Update runtime limits."""
        self._limits.update(kwargs)

    def health(self) -> dict[str, Any]:
        """Get runtime health status."""
        return {
            "status": "healthy" if len(self._running) < self._limits["max_concurrent"] else "degraded",
            "active_tasks": len(self._running),
            "total_tasks": len(self._tasks),
            **self.get_statistics(),
            "timestamp": datetime.now(UTC).isoformat(),
        }
