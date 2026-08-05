"""AIOS Task Runtime — executes plain async tasks.

A task is a callable accepting a context dict. The task runtime adds
timeout, retry policy and outcome recording.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any

from .runtime import BaseRuntime, RuntimeCallable


class TaskRuntime(BaseRuntime):
    """Run tasks with optional timeout and retries."""

    kind = "task"

    def __init__(self, name: str = "task-runtime", *, timeout: float = 30.0, max_retries: int = 0) -> None:
        super().__init__(name, limits={"timeout": timeout, "max_retries": max_retries})
        self._results: dict[str, dict[str, Any]] = {}

    async def run(self, target: RuntimeCallable, context: dict[str, Any]) -> dict[str, Any]:
        task_id = context.pop("task_id", f"task-{uuid.uuid4().hex[:10]}")
        timeout = float(self.limits.get("timeout", 30.0))
        max_retries = int(self.limits.get("max_retries", 0))
        started = time.perf_counter()
        last_error: str | None = None
        attempt = 0
        while attempt <= max_retries:
            attempt += 1
            try:
                result = target(context)
                if asyncio.iscoroutine(result):
                    result = await asyncio.wait_for(result, timeout=timeout)
                outcome = {
                    "ok": True,
                    "task_id": task_id,
                    "attempts": attempt,
                    "result": result,
                    "error": None,
                    "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                }
                self._results[task_id] = outcome
                return outcome
            except asyncio.TimeoutError:
                last_error = f"timeout after {timeout}s"
            except Exception as exc:  # noqa: BLE001
                last_error = f"{type(exc).__name__}: {exc}"
        outcome = {
            "ok": False,
            "task_id": task_id,
            "attempts": attempt,
            "result": None,
            "error": last_error,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
        }
        self._results[task_id] = outcome
        return outcome

    def results(self) -> dict[str, dict[str, Any]]:
        return dict(self._results)
