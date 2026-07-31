"""Health check engine."""

from __future__ import annotations

import time
from typing import Any


class HealthEngine:
    def __init__(self) -> None:
        self._checks: dict[str, Any] = {}
        self._results: dict[str, dict[str, Any]] = {}
        self._started = False

    def start(self) -> None:
        self._started = True

    def stop(self) -> None:
        self._started = False

    def register_check(self, name: str, check_func: Any) -> None:
        self._checks[name] = check_func

    def run_check(self, name: str) -> dict[str, Any]:
        check = self._checks.get(name)
        if not check:
            return {"status": "unknown", "message": "check_not_found"}
        try:
            start = time.time()
            check()
            elapsed = (time.time() - start) * 1000
            self._results[name] = {"status": "healthy", "latency_ms": elapsed, "timestamp": time.time()}
            return self._results[name]
        except Exception as e:
            self._results[name] = {"status": "unhealthy", "error": str(e), "timestamp": time.time()}
            return self._results[name]

    def run_all(self) -> dict[str, dict[str, Any]]:
        for name in self._checks:
            self.run_check(name)
        return dict(self._results)

    def get_status(self) -> dict[str, Any]:
        return {"running": self._started, "checks": len(self._checks), "last_results": len(self._results)}

    def get_result(self, name: str) -> dict[str, Any] | None:
        return self._results.get(name)

    def get_overall_health(self) -> str:
        if not self._results:
            return "unknown"
        statuses = [r.get("status") for r in self._results.values()]
        if all(s == "healthy" for s in statuses):
            return "healthy"
        if any(s == "unhealthy" for s in statuses):
            return "unhealthy"
        return "degraded"
