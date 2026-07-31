"""Incident report."""

from __future__ import annotations

import time
from typing import Any


class IncidentReport:
    def __init__(self) -> None:
        self._incidents: list[dict[str, Any]] = []

    def add_incident(self, incident: dict[str, Any]) -> None:
        self._incidents.append(incident)

    def get_summary(self) -> dict[str, Any]:
        total = len(self._incidents)
        by_severity: dict[str, int] = {}
        for inc in self._incidents:
            sev = inc.get("severity", "unknown")
            by_severity[sev] = by_severity.get(sev, 0) + 1
        return {"total": total, "by_severity": by_severity, "timestamp": time.time()}

    def generate_report(self, period: str = "all") -> dict[str, Any]:
        return {"period": period, "summary": self.get_summary(), "incidents": self._incidents[-50:]}

    def list_incidents(self, severity: str = "", limit: int = 100) -> list[dict[str, Any]]:
        results = self._incidents
        if severity:
            results = [i for i in results if i.get("severity") == severity]
        return results[-limit:]

    def count(self) -> int:
        return len(self._incidents)

    def clear(self) -> int:
        n = len(self._incidents)
        self._incidents.clear()
        return n
