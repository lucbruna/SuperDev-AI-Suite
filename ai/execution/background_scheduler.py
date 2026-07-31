from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any

from agents.communication.message_bus import MessageBus


class BackgroundScheduler:
    def __init__(self, message_bus: MessageBus | None = None):
        self._bus = message_bus or MessageBus()
        self._tasks: dict[str, dict[str, Any]] = {}
        self._running_tasks: dict[str, asyncio.Task] = {}
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()

    async def start(self):
        asyncio.create_task(self._process_queue())

    async def enqueue(self, task: dict[str, Any]) -> str:
        task_id = f"bg_{uuid.uuid4().hex[:12]}"
        task["task_id"] = task_id
        task["status"] = "queued"
        task["created_at"] = datetime.utcnow().isoformat()
        task["progress"] = 0
        self._tasks[task_id] = task
        await self._queue.put(task)
        await self._bus.publish("background.task.queued", {"task_id": task_id, "name": task.get("name", "")})
        return task_id

    async def _process_queue(self):
        while True:
            task = await self._queue.get()
            task_id = task["task_id"]
            self._tasks[task_id]["status"] = "running"
            await self._bus.publish("background.task.started", {"task_id": task_id})

            try:
                handler = task.get("handler")
                if handler:
                    result = await handler(task.get("params", {}))
                    self._tasks[task_id]["status"] = "completed"
                    self._tasks[task_id]["completed_at"] = datetime.utcnow().isoformat()
                    self._tasks[task_id]["result"] = result
                    await self._bus.publish("background.task.completed", {"task_id": task_id, "result": result})
                else:
                    self._tasks[task_id]["status"] = "failed"
                    self._tasks[task_id]["error"] = "No handler provided"
            except Exception as e:
                self._tasks[task_id]["status"] = "failed"
                self._tasks[task_id]["error"] = str(e)
                await self._bus.publish("background.task.failed", {"task_id": task_id, "error": str(e)})

    async def get_task(self, task_id: str) -> dict[str, Any] | None:
        return self._tasks.get(task_id)

    async def list_tasks(self, status: str | None = None) -> list[dict[str, Any]]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        return sorted(tasks, key=lambda t: t.get("created_at", ""), reverse=True)

    async def cancel_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.get("status") in ("queued", "running"):
            task["status"] = "cancelled"
            await self._bus.publish("background.task.cancelled", {"task_id": task_id})
            return True
        return False

    async def update_progress(self, task_id: str, progress: int, message: str = "") -> None:
        task = self._tasks.get(task_id)
        if task:
            task["progress"] = min(100, max(0, progress))
            if message:
                task["progress_message"] = message
            await self._bus.publish(
                "background.task.progress", {"task_id": task_id, "progress": progress, "message": message}
            )
