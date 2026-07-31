"""Health checks for integrated systems."""

from __future__ import annotations

import time
from typing import Any, Callable

_STATUS = {"up", "down", "degraded"}


class HealthCheck:
    """Runs health probes against connectors and services."""

    def __init__(self) -> None:
        self._probes: dict[str, Callable[[], bool]] = {}
        self._results: dict[str, dict[str, Any]] = {}

    def register(self, name: str, probe: Callable[[], bool]) -> None:
        self._probes[name] = probe

    def check(self, name: str) -> str:
        probe = self._probes.get(name)
        if probe is None:
            return "down"
        try:
            ok = probe()
        except Exception:
            ok = False
        status = "up" if ok else "down"
        self._results[name] = {"status": status, "checked_at": time.time()}
        return status

    def check_all(self) -> dict[str, str]:
        return {name: self.check(name) for name in self._probes}

    def status(self, name: str) -> str:
        return self._results.get(name, {}).get("status", "down")

    def overall(self) -> str:
        statuses = self.check_all().values()
        if not statuses:
            return "down"
        if all(s == "up" for s in statuses):
            return "up"
        if any(s == "down" for s in statuses):
            return "degraded"
        return "up"
