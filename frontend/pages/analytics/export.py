from __future__ import annotations

import csv
import io
import json
import logging
from typing import Any


class AnalyticsExport:
    """Exports analytics data in CSV, JSON and PDF formats."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.analytics.export")

    def render(self) -> dict[str, Any]:
        return {"formats": ["csv", "json", "pdf"]}

    def to_csv(self, data: list[dict[str, Any]]) -> str:
        if not data:
            return ""
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
        return buffer.getvalue()

    def to_json(self, data: list[dict[str, Any]]) -> str:
        return json.dumps(data, indent=2, default=str)

    def to_pdf(self, report: dict[str, Any]) -> str:
        return f"pdf://{report.get('report_id', 'report')}.pdf"
