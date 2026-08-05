"""AIOS Kernel Monitor — component state tracking and health probes.

Each component can register a ``check`` callable returning a status
dict; the monitor aggregates them into a deterministic report.
"""

from __future__ import annotations

import time
from typing import Any, Callable

Status = dict[str, Any]
Check = Callable[[], Status]


class KernelMonitor:
    """Registry of named checks plus a status ledger."""

    def __init__(self) -> None:
        self._checks: dict[str, Check] = {}
        self._ledger: dict[str, Status] = {}

    def register(self, name: str, check: Check) -> "KernelMonitor":
        self._checks[name] = check
        return self

    def unregister(self, name: str) -> None:
        self._checks.pop(name, None)
        self._ledger.pop(name, None)

    def run_check(self, name: str) -> Status:
        check = self._checks[name]
        started = time.perf_counter()
        try:
            status = check()
            status.setdefault("status", "ok")
        except Exception as exc:  # noqa: BLE001 - probe must never raise
            status = {"status": "error", "error": f"{type(exc).__name__}: {exc}"}
        status["checked_at"] = time.time()
        status["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 3)
        self._ledger[name] = status
        return status

    def check_all(self) -> dict[str, Status]:
        return {name: self.run_check(name) for name in sorted(self._checks)}

    def report(self) -> dict[str, Any]:
        results = self.check_all()
        by_status: dict[str, int] = {}
        for item in results.values():
            by_status[item["status"]] = by_status.get(item["status"], 0) + 1
        return {
            "checks": results,
            "summary": by_status,
            "healthy": all(item["status"] == "ok" for item in results.values()) if results else True,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"registered": sorted(self._checks), "ledger": dict(self._ledger)}
