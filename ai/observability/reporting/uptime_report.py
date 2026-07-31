"""Uptime report."""

from __future__ import annotations

import time
from typing import Any


class UptimeReport:
    def __init__(self) -> None:
        self._checks: dict[str, list[dict[str, Any]]] = {}

    def record_check(self, service: str, status: str) -> None:
        self._checks.setdefault(service, []).append({"status": status, "timestamp": time.time()})

    def get_uptime(self, service: str) -> float:
        checks = self._checks.get(service, [])
        if not checks:
            return 0.0
        total = len(checks)
        up = sum(1 for c in checks if c["status"] == "healthy")
        return (up / total) * 100

    def get_all_uptime(self) -> dict[str, float]:
        return {service: self.get_uptime(service) for service in self._checks}

    def generate_report(self) -> dict[str, Any]:
        return {"services": self.get_all_uptime(), "total_services": len(self._checks), "timestamp": time.time()}

    def list_services(self) -> list[str]:
        return list(self._checks.keys())

    def get_service_history(self, service: str, limit: int = 100) -> list[dict[str, Any]]:
        return self._checks.get(service, [])[-limit:]
