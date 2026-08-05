"""Avatar scheduler — queue avatar/render tasks with priority."""
from __future__ import annotations

from typing import Any


class AvatarScheduler:
    """Priority-ordered task queue for avatar pipeline jobs."""

    def __init__(self) -> None:
        self._queue: list[dict[str, Any]] = []
        self._running: list[str] = []
        self._counter = 0

    def enqueue(self, task: dict[str, Any], *, priority: int = 5) -> str:
        self._counter += 1
        task_id = task.setdefault("id", f"avatar_task_{self._counter}")
        task["priority"] = priority
        self._queue.append(task)
        self._queue.sort(key=lambda t: (t["priority"], t["id"]))
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

    def cancel(self, task_id: str) -> bool:
        for i, task in enumerate(self._queue):
            if task["id"] == task_id:
                self._queue.pop(i)
                return True
        return False

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
