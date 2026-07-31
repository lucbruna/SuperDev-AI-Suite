from __future__ import annotations

import logging
import time
from typing import Any

from ..integration_models import ConnectorStatus, HealthReport


class ConnectorHealth:
    """Health checks for connectors and connections."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.connectors.health")
        self._reports: dict[str, HealthReport] = {}

    def check(self, component: str, probe: Any) -> HealthReport:
        """Runs a probe (a callable returning a dict) and records a report."""
        start = time.monotonic()
        try:
            result = probe()
            status = "ok" if result.get("ok", True) else "error"
            message = str(result.get("message", ""))
        except Exception as exc:  # noqa: BLE001
            status = "error"
            message = str(exc)
            result = {}
        latency = (time.monotonic() - start) * 1000
        report = HealthReport(
            component=component,
            status=status,
            latency_ms=round(latency, 3),
            message=message,
            metadata=dict(result),
        )
        self._reports[component] = report
        return report

    def check_connector(self, connection_id: str, connector: Any) -> HealthReport:
        def _probe() -> dict[str, Any]:
            if not connector.is_connected():
                return {"ok": False, "message": "not connected"}
            tested = connector.test()
            return {"ok": tested, "message": "" if tested else "test failed"}

        return self.check(f"connection:{connection_id}", _probe)

    def get(self, component: str) -> HealthReport | None:
        return self._reports.get(component)

    def all(self) -> list[HealthReport]:
        return list(self._reports.values())

    def unhealthy(self) -> list[HealthReport]:
        return [report for report in self._reports.values() if report.status != "ok"]

    def snapshot(self) -> dict[str, Any]:
        reports = self.all()
        return {
            "total": len(reports),
            "healthy": sum(1 for r in reports if r.status == "ok"),
            "unhealthy": sum(1 for r in reports if r.status != "ok"),
        }
