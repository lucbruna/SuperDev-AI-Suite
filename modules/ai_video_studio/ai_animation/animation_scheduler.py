"""Animation scheduler — queue animation rendering tasks."""
from __future__ import annotations

from typing import Any


class AnimationScheduler:
    """Schedules animation render tasks with priority."""

    def __init__(self) -> None:
        self._queue: list[dict[str, Any]] = []
        self._running: list[str] = []

    def enqueue(self, task: dict[str, Any], *, priority: int = 5) -> str:
        task["priority"] = priority
        task_id = task.setdefault("id", f"anim_task_{len(self._queue) + 1}")
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


_animation_scheduler: AnimationScheduler | None = None


def get_animation_scheduler() -> AnimationScheduler:
    global _animation_scheduler
    if _animation_scheduler is None:
        _animation_scheduler = AnimationScheduler()
    return _animation_scheduler
