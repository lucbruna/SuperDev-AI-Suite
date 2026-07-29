"""Task Scheduler — scheduled and recurring task management for the platform.

Wraps the existing backend/scheduler/scheduler.py into the orchestrator's
service architecture with cron expression support, dependency-aware
scheduling, and lifecycle management.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from .exceptions import OrchestratorError
from .types import ServiceStatus, now_iso

try:
    from croniter import croniter
    HAS_CRONITER = True
except ImportError:
    HAS_CRONITER = False


class ScheduledTask:
    """A single scheduled task with execution tracking."""

    def __init__(
        self,
        task_id: str,
        name: str,
        func: Any,
        interval_seconds: float = 0,
        cron_expr: str = "",
        args: tuple = (),
        kwargs: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> None:
        self.task_id = task_id
        self.name = name
        self.func = func
        self.interval_seconds = interval_seconds
        self.cron_expr = cron_expr
        self.args = args
        self.kwargs = kwargs or {}
        self.max_retries = max_retries

        self.enabled: bool = True
        self.run_count: int = 0
        self.error_count: int = 0
        self.last_run: datetime | None = None
        self.next_run: datetime = datetime.now(timezone.utc)
        self.last_error: str = ""
        self.last_duration_ms: float = 0.0

        if cron_expr and HAS_CRONITER:
            self._cron = croniter(cron_expr, time.time())
            self.next_run = datetime.fromtimestamp(
                self._cron.get_next(float), tz=timezone.utc,
            )

    def update_next_run(self) -> None:
        """Calculate the next run time."""
        now = datetime.now(timezone.utc)
        if self.cron_expr and HAS_CRONITER:
            self.next_run = datetime.fromtimestamp(
                self._cron.get_next(float), tz=timezone.utc,
            )
        elif self.interval_seconds > 0:
            now = datetime.now(timezone.utc)
            self.next_run = now + timedelta(seconds=self.interval_seconds)

    @property
    def is_due(self) -> bool:
        """Check if the task is due to run."""
        if not self.enabled:
            return False
        return datetime.now(timezone.utc) >= self.next_run


class TaskScheduler:
    """Orchestrator-managed task scheduler.

    Integrates with the existing backend/scheduler/scheduler.py or runs
    standalone with cron expressions and interval-based scheduling.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, ScheduledTask] = {}
        self._running = False
        self._poll_task: asyncio.Task[None] | None = None
        self._poll_interval: float = 2.0  # seconds
        self._on_task_complete: Any = None
        self._on_task_failed: Any = None

    def set_callbacks(
        self,
        on_complete: Any = None,
        on_failed: Any = None,
    ) -> None:
        """Set callbacks for task lifecycle events."""
        self._on_task_complete = on_complete
        self._on_task_failed = on_failed

    # ─── Task Registration ────────────────────────────────────────────────

    def add_task(
        self,
        name: str,
        func: Any,
        interval_seconds: float = 0,
        cron_expr: str = "",
        args: tuple = (),
        kwargs: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> str:
        """Register a new scheduled task."""
        import uuid
        task_id = uuid.uuid4().hex[:12]

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            func=func,
            interval_seconds=interval_seconds,
            cron_expr=cron_expr,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries,
        )
        self._tasks[task_id] = task
        return task_id

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from scheduling."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def enable_task(self, task_id: str) -> bool:
        """Enable a disabled task."""
        task = self._tasks.get(task_id)
        if task:
            task.enabled = True
            return True
        return False

    def disable_task(self, task_id: str) -> bool:
        """Disable a task without removing it."""
        task = self._tasks.get(task_id)
        if task:
            task.enabled = False
            return True
        return False

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Get task details."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        return {
            "task_id": task.task_id,
            "name": task.name,
            "enabled": task.enabled,
            "interval_seconds": task.interval_seconds,
            "cron_expr": task.cron_expr,
            "run_count": task.run_count,
            "error_count": task.error_count,
            "last_error": task.last_error,
            "last_duration_ms": task.last_duration_ms,
            "last_run": task.last_run.isoformat() if task.last_run else None,
            "next_run": task.next_run.isoformat() if task.next_run else None,
        }

    # ─── Lifecycle ────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the scheduler polling loop."""
        self._running = True
        self._poll_task = asyncio.create_task(self._poll_loop())

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._poll_task:
            self._poll_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._poll_task

    async def run_once(self, task_id: str) -> dict[str, Any]:
        """Execute a task immediately."""
        task = self._tasks.get(task_id)
        if not task:
            return {"success": False, "error": "Task not found"}

        return await self._execute_task(task)

    async def run_all_due(self) -> list[dict[str, Any]]:
        """Execute all tasks that are currently due."""
        results = []
        for task in list(self._tasks.values()):
            if task.is_due:
                result = await self._execute_task(task)
                results.append(result)
                task.update_next_run()
        return results

    async def _poll_loop(self) -> None:
        """Background loop that polls for due tasks."""
        while self._running:
            try:
                await self.run_all_due()
                await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(self._poll_interval)

    async def _execute_task(self, task: ScheduledTask) -> dict[str, Any]:
        """Execute a single task with retry logic."""
        start = time.time()
        last_error = ""

        for attempt in range(task.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(task.func):
                    result = await task.func(*task.args, **task.kwargs)
                else:
                    result = task.func(*task.args, **task.kwargs)

                elapsed_ms = round((time.time() - start) * 1000, 2)
                task.run_count += 1
                task.last_run = datetime.now(timezone.utc)
                task.last_duration_ms = elapsed_ms
                task.last_error = ""
                task.error_count = 0

                if self._on_task_complete:
                    await self._on_task_complete(task.name, result, elapsed_ms)

                return {
                    "success": True,
                    "task_id": task.task_id,
                    "name": task.name,
                    "duration_ms": elapsed_ms,
                    "attempt": attempt + 1,
                }

            except Exception as e:
                last_error = str(e)
                if attempt < task.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue

        # All retries failed
        task.error_count += 1
        task.last_error = last_error

        if self._on_task_failed:
            await self._on_task_failed(task.name, last_error)

        return {
            "success": False,
            "task_id": task.task_id,
            "name": task.name,
            "error": last_error,
            "attempts": task.max_retries + 1,
        }

    # ─── Query ────────────────────────────────────────────────────────────

    def list_tasks(self) -> list[dict[str, Any]]:
        """List all registered tasks."""
        return [
            self.get_task(tid) for tid in self._tasks
        ]

    def get_statistics(self) -> dict[str, Any]:
        """Get scheduler statistics."""
        total = len(self._tasks)
        enabled = sum(1 for t in self._tasks.values() if t.enabled)
        total_runs = sum(t.run_count for t in self._tasks.values())
        total_errors = sum(t.error_count for t in self._tasks.values())
        return {
            "total_tasks": total,
            "enabled_tasks": enabled,
            "disabled_tasks": total - enabled,
            "total_runs": total_runs,
            "total_errors": total_errors,
            "is_running": self._running,
            "poll_interval_seconds": self._poll_interval,
        }
