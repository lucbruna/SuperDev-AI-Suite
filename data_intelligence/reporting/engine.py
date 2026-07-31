"""Reporting engine (attached by the facade as ``reporting``).

Implements ``ReportGenerator.generate``: assembles a report from template
and data, renders it in the chosen format and stores the result.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import ReportFormat, ReportSpec
from data_intelligence.reporting.base import ReportingError
from data_intelligence.reporting.formats import render_report
from data_intelligence.reporting.scheduler import ReportScheduler
from data_intelligence.reporting.templates import get_template


class ReportingEngine:
    """Coordinates report specs, generation and scheduling."""

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.specs: dict[str, ReportSpec] = {}
        self.results: dict[str, dict[str, Any]] = {}
        self.scheduler = ReportScheduler()

    def register(self, report_id: str, name: str,
                 report_type: str = "executive",
                 format: ReportFormat = ReportFormat.JSON,
                 schedule_cron: str | None = None) -> ReportSpec:
        spec = ReportSpec(report_id=report_id, name=name,
                          report_type=report_type, format=format,
                          schedule_cron=schedule_cron)
        self.specs[report_id] = spec
        if schedule_cron:
            self.scheduler.schedule(report_id, schedule_cron)
        return spec

    def remove(self, report_id: str) -> bool:
        self.results.pop(report_id, None)
        self.scheduler.jobs.pop(report_id, None)
        return self.specs.pop(report_id, None) is not None

    def generate(self, report_id: str,
                 data: dict[str, Any]) -> dict[str, Any]:
        """Builds, renders and stores the report (ReportGenerator API)."""
        spec = self.specs.get(report_id)
        if spec is None:
            raise ReportingError(f"unknown report: {report_id}")
        template = get_template(spec.report_type)
        sections = template.instantiate(data) if template else {
            "name": spec.report_type, "sections": []}
        tables = self._tables_from_sections(sections["sections"])
        payload: dict[str, Any] = {
            "report_id": report_id, "name": spec.name,
            "type": spec.report_type, "summary": data.get("summary", {}),
            "tables": tables,
            "generated_at": datetime.now().isoformat(),
        }
        rendered = render_report(spec.format, payload)
        result = {"report_id": report_id, "name": spec.name,
                  "format": spec.format.value, "payload": payload,
                  "content": rendered}
        self.results[report_id] = result
        self.metrics.increment("reporting.generated")
        self.events.publish(DataIntelligenceEventType.REPORT_GENERATED,
                            {"report_id": report_id})
        return result

    def run_due(self, now: datetime | None = None) -> list[dict[str, Any]]:
        """Generates every scheduled report that is due right now."""
        generated: list[dict[str, Any]] = []
        for report_id in list(self.scheduler.jobs):
            if self.scheduler.due(report_id, now):
                result = self.generate(report_id, {})
                self.scheduler.mark_run(report_id)
                generated.append(result)
        return generated

    def latest(self, report_id: str) -> dict[str, Any] | None:
        return self.results.get(report_id)

    def _tables_from_sections(self,
                              sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tables: list[dict[str, Any]] = []
        for section in sections:
            data = section.get("data")
            if isinstance(data, dict) and "rows" in data:
                tables.append({"title": section["title"],
                               "columns": data.get("columns", []),
                               "rows": data["rows"]})
            elif isinstance(data, list):
                if data and all(isinstance(item, dict) for item in data):
                    columns = list(data[0].keys())
                    tables.append({"title": section["title"],
                                   "columns": columns, "rows": data})
        return tables

    def stats(self) -> dict[str, Any]:
        return {"reports": list(self.specs),
                "generated": len(self.results),
                "scheduled": self.scheduler.list_jobs()}
