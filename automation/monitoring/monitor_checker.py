"""Runs registered health checks."""

from __future__ import annotations

import time
from typing import Any, Callable

from automation.monitoring.monitor_models import MonitorCheck, MonitorStatus

Probe = Callable[[], bool | tuple[bool, str]]


class MonitorChecker:
    """Registers probes and executes them on demand."""

    def __init__(self) -> None:
        self._probes: dict[str, tuple[str, Probe]] = {}

    def register(self, check_id: str, name: str, probe: Probe) -> None:
        self._probes[check_id] = (name, probe)

    def run(self, check_id: str) -> MonitorCheck | None:
        entry = self._probes.get(check_id)
        if entry is None:
            return None
        name, probe = entry
        try:
            result = probe()
            if isinstance(result, tuple):
                ok, detail = bool(result[0]), str(result[1])
            else:
                ok, detail = bool(result), ""
            status = MonitorStatus.HEALTHY if ok else MonitorStatus.CRITICAL
        except Exception as exc:  # noqa: BLE001
            status, detail = MonitorStatus.CRITICAL, str(exc)
        return MonitorCheck(check_id, name, status, detail, time.time())

    def run_all(self) -> list[MonitorCheck]:
        checks: list[MonitorCheck] = []
        for check_id in self._probes:
            check = self.run(check_id)
            if check is not None:
                checks.append(check)
        return checks

    def ids(self) -> list[str]:
        return list(self._probes)
