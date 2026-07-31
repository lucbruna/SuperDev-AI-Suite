"""Service health checks."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class ServiceCheck:
    def __init__(self) -> None:
        self._services: dict[str, Callable[[], bool]] = {}
        self._results: dict[str, dict[str, Any]] = {}

    def register(self, name: str, check_func: Callable[[], bool]) -> None:
        self._services[name] = check_func

    def check(self, name: str) -> dict[str, Any]:
        func = self._services.get(name)
        if not func:
            return {"service": name, "status": "unknown", "message": "not_registered"}
        try:
            start = time.time()
            healthy = func()
            elapsed = (time.time() - start) * 1000
            result = {"service": name, "status": "healthy" if healthy else "unhealthy", "latency_ms": elapsed}
        except Exception as e:
            result = {"service": name, "status": "error", "error": str(e)}
        self._results[name] = result
        return result

    def check_all(self) -> dict[str, dict[str, Any]]:
        for name in self._services:
            self.check(name)
        return dict(self._results)

    def list_services(self) -> list[str]:
        return list(self._services.keys())

    def get_result(self, name: str) -> dict[str, Any]:
        return self._results.get(name, {})
