"""Skill scheduler — interval-based scheduling of skill executions."""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class ScheduledTask:
    skill_id: str
    interval_s: float
    enabled: bool = True
    runs: int = 0
    last_run_at: str | None = None
    last_error: str | None = None


class SkillScheduler:
    """Registers interval tasks; a background loop executes them when running."""

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._loop_task: asyncio.Task | None = None

    def schedule(self, skill_id: str, interval_s: float) -> dict[str, Any]:
        if interval_s <= 0:
            raise ValueError("interval_s must be positive")
        task = ScheduledTask(skill_id=skill_id, interval_s=interval_s)
        self._tasks[skill_id] = task
        return {"skill_id": skill_id, "interval_s": interval_s, "scheduled": True}

    def unschedule(self, skill_id: str) -> bool:
        return self._tasks.pop(skill_id, None) is not None

    def start(self, runner) -> None:  # type: ignore[no-untyped-def]
        """Start the background loop; ``runner`` is an awaitable executor."""
        if self._loop_task is None or self._loop_task.done():
            self._loop_task = asyncio.create_task(self._run_loop(runner))

    def stop(self) -> None:
        if self._loop_task is not None:
            self._loop_task.cancel()
            self._loop_task = None

    async def _run_loop(self, runner) -> None:  # type: ignore[no-untyped-def]
        try:
            while True:
                for task in self._tasks.values():
                    if not task.enabled:
                        continue
                    try:
                        await runner(task.skill_id)
                        task.runs += 1
                        task.last_error = None
                    except Exception as e:  # noqa: BLE001 — scheduler keeps ticking
                        task.last_error = str(e)
                    task.last_run_at = datetime.now(UTC).isoformat()
                await asyncio.sleep(1.0)
        except asyncio.CancelledError:
            return

    def snapshot(self) -> dict[str, Any]:
        return {
            "running": self._loop_task is not None and not self._loop_task.done(),
            "tasks": [
                {
                    "skill_id": t.skill_id,
                    "interval_s": t.interval_s,
                    "enabled": t.enabled,
                    "runs": t.runs,
                    "last_run_at": t.last_run_at,
                    "last_error": t.last_error,
                }
                for t in self._tasks.values()
            ],
        }


_scheduler: SkillScheduler | None = None


def get_skill_scheduler() -> SkillScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = SkillScheduler()
    return _scheduler
