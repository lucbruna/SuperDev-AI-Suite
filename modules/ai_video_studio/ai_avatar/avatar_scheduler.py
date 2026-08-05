"""Avatar scheduler — queue presenter render tasks by priority."""
from __future__ import annotations

from typing import Any


class AvatarScheduler:
    """Schedules avatar render tasks with priority ordering."""

    def __init__(self) -> None:
        self._queue: list[dict[str, Any]] = []
        self._running: list[str] = []

    def enqueue(self, task: dict[str, Any], *, priority: int = 5) -> str:
        task["priority"] = priority
        task_id = task.setdefault("id", f"avatar_task_{len(self._queue) + 1}")
        self._queue.append(task)
        self._queue.sort(key=lambda t: t["priority"])
        return task_id

    def next(self) -> dict[str, Any] | None:
        if not self._queue:
            return None
        task = self._queue.pop(0)
        self._running.append(task["id"])
        return task

    def complete(self, task_id: str) -> None:
        if task_id in self._running:
            self._running.remove(task_id)

    def pending(self) -> int:
        return len(self._queue)

    def running_count(self) -> int:
        return len(self._running)


_avatar_scheduler: AvatarScheduler | None = None


def get_avatar_scheduler() -> AvatarScheduler:
    global _avatar_scheduler
    if _avatar_scheduler is None:
        _avatar_scheduler = AvatarScheduler()
    return _avatar_scheduler
