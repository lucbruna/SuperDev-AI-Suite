from __future__ import annotations

import logging
from typing import Any


class AnalyticsReports:
    """Report catalog with detail and export."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.analytics.reports")
        self._reports: dict[str, dict[str, Any]] = {}

    def render(self) -> dict[str, Any]:
        return {"reports": self.list(), "count": len(self._reports)}

    def list(self) -> list[dict[str, Any]]:
        return [
            {"report_id": report_id, **report}
            for report_id, report in self._reports.items()
        ]

    def detail(self, report_id: str) -> dict[str, Any]:
        report = self._reports.get(report_id)
        if report is None:
            raise KeyError(f"unknown report: {report_id}")
        return dict(report)

    def export(self, report_id: str, fmt: str = "csv") -> str:
        if report_id not in self._reports:
            raise KeyError(f"unknown report: {report_id}")
        return f"export://{report_id}.{fmt}"
