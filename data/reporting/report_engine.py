from __future__ import annotations

import time
from typing import Any

from ..data_models import Report, ReportFormat


class ReportEngine:
    """Automatic reporting — executive, technical, financial, operational reports with export and scheduling."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.reporting
        self._reports: dict[str, Report] = {}
        self._schedules: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    async def create_report(
        self,
        title: str,
        kind: str = "executive",
        data: dict[str, Any] | None = None,
    ) -> Report:
        report = Report(
            title=title,
            kind=kind,
            format=ReportFormat(self.config.default_format),
            data=data or {},
        )
        report.sections = self._build_sections(kind, report.data)
        self._reports[report.report_id] = report
        self.engine.registry.register_report(report)
        self.engine.metrics.increment("reporting.reports", labels={"kind": kind})
        await self.engine.event_bus.emit("data.report_created", {
            "report_id": report.report_id,
            "kind": kind,
        })
        return report

    def _build_sections(self, kind: str, data: dict[str, Any]) -> list[dict[str, Any]]:
        if kind == "executive":
            return [
                {"title": "Overview", "content": self._summary(data)},
                {"title": "KPIs", "content": data.get("kpis", {})},
                {"title": "Recommendations", "content": data.get("recommendations", [])},
            ]
        if kind == "financial":
            return [
                {"title": "Revenue", "content": data.get("revenue", 0)},
                {"title": "Costs", "content": data.get("costs", 0)},
                {"title": "Margin", "content": data.get("margin", 0)},
            ]
        if kind == "technical":
            return [
                {"title": "System Status", "content": data.get("system_status", {})},
                {"title": "Errors", "content": data.get("errors", [])},
            ]
        return [{"title": "Operational Metrics", "content": data}]

    @staticmethod
    def _summary(data: dict[str, Any]) -> str:
        items = [f"{k}: {v}" for k, v in data.items()]
        return "; ".join(items) if items else "No data available"

    def get_report(self, report_id: str) -> Report | None:
        return self._reports.get(report_id)

    def list_reports(self) -> list[Report]:
        return list(self._reports.values())

    def render(self, report: Report) -> str:
        """Render the report in its configured format (markdown/html/json)."""
        if report.format == ReportFormat.HTML:
            sections = "".join(
                f"<h2>{s['title']}</h2><p>{s['content']}</p>"
                for s in report.sections
            )
            return f"<html><body><h1>{report.title}</h1>{sections}</body></html>"
        if report.format == ReportFormat.JSON:
            import json
            return json.dumps({
                "title": report.title,
                "kind": report.kind,
                "sections": report.sections,
                "data": report.data,
            })
        lines = [f"# {report.title}", ""]
        for section in report.sections:
            lines.append(f"## {section['title']}")
            lines.append(str(section["content"]))
            lines.append("")
        return "\n".join(lines)

    def export(self, report_id: str, target_format: str = "markdown") -> str | None:
        report = self._reports.get(report_id)
        if not report:
            return None
        report.format = ReportFormat(target_format)
        return self.render(report)

    def schedule(self, report_id: str, cron: str) -> bool:
        if report_id not in self._reports:
            return False
        self._schedules[report_id] = {"cron": cron, "created_at": time.time()}
        return True

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "reports": len(self._reports),
            "schedules": len(self._schedules),
        }


__all__ = ["ReportEngine"]
