"""AIOS Kernel Runtime — async job runner.

Runs callables / coroutine factories with an optional timeout and
records execution results in a deterministic way. The runtime is the
single entry point for executing platform jobs from the kernel.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from typing import Any, Awaitable, Callable

Job = Callable[[], Awaitable[Any]]


class KernelRuntime:
    """Execute async jobs with timeout, tracking outcomes."""

    def __init__(self, default_timeout: float = 30.0) -> None:
        self.default_timeout = default_timeout
        self._results: dict[str, dict[str, Any]] = {}

    async def run(
        self,
        job: Job,
        *,
        timeout: float | None = None,
        job_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run a coroutine factory, guarding it with an optional timeout.

        Returns ``{"ok": bool, "job_id": str, "result": Any|None, "error": str|None, "elapsed_ms": float}``
        """
        jid = job_id or f"job-{uuid.uuid4().hex[:10]}"
        started = time.perf_counter()
        limit = self.default_timeout if timeout is None else timeout
        try:
            coro = job()
            if asyncio.iscoroutine(coro):
                if limit > 0:
                    result = await asyncio.wait_for(coro, timeout=limit)
                else:
                    result = await coro
            else:
                result = coro
            outcome = {
                "ok": True,
                "job_id": jid,
                "result": result,
                "error": None,
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                "metadata": metadata or {},
            }
        except asyncio.TimeoutError:
            outcome = {
                "ok": False,
                "job_id": jid,
                "result": None,
                "error": f"timeout after {limit}s",
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                "metadata": metadata or {},
            }
        except Exception as exc:  # noqa: BLE001 - boundary records any failure
            outcome = {
                "ok": False,
                "job_id": jid,
                "result": None,
                "error": f"{type(exc).__name__}: {exc}",
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                "metadata": metadata or {},
            }
        self._results[jid] = outcome
        return outcome

    def results(self) -> dict[str, dict[str, Any]]:
        return dict(self._results)

    def clear(self) -> None:
        self._results.clear()

    def summary(self) -> dict[str, Any]:
        ok_count = sum(1 for r in self._results.values() if r["ok"])
        return {
            "total": len(self._results),
            "ok": ok_count,
            "failed": len(self._results) - ok_count,
        }
