"""Report generator."""
import uuid
from datetime import datetime
from typing import Any

from .models import (
    GeneratedReport,
    ReportFormat,
    ReportSchedule,
    ReportTemplate,
)


class ReportGenerator:
    def __init__(self):
        self._templates: dict[str, ReportTemplate] = {}
        self._reports: dict[str, GeneratedReport] = {}
        self._schedules: dict[str, ReportSchedule] = {}

    def create_template(self, template: ReportTemplate) -> ReportTemplate:
        self._templates[template.template_id] = template
        return template

    def get_template(self, template_id: str) -> ReportTemplate | None:
        return self._templates.get(template_id)

    def list_templates(self) -> list[ReportTemplate]:
        return list(self._templates.values())

    def generate_report(self, template_id: str, data: dict[str, Any], format: ReportFormat = ReportFormat.HTML) -> GeneratedReport:
        template = self._templates.get(template_id)
        if not template:
            return GeneratedReport(
                report_id=str(uuid.uuid4()),
                template_id=template_id,
                format=format,
                error=f"Template {template_id} not found",
            )
        report_data = {
            "template_name": template.name,
            "report_type": template.report_type.value,
            "sections": [],
            "generated_at": datetime.now().isoformat(),
        }
        for section in template.sections:
            section_data = {
                "id": section.section_id,
                "title": section.title,
                "type": section.section_type,
                "content": data.get(section.section_id, section.content),
            }
            report_data["sections"].append(section_data)
        report_id = str(uuid.uuid4())
        report = GeneratedReport(
            report_id=report_id,
            template_id=template_id,
            format=format,
            data=report_data,
            size_bytes=len(str(report_data)),
            generated_at=datetime.now(),
        )
        self._reports[report_id] = report
        return report

    def get_report(self, report_id: str) -> GeneratedReport | None:
        return self._reports.get(report_id)

    def list_reports(self, template_id: str | None = None) -> list[GeneratedReport]:
        reports = list(self._reports.values())
        if template_id:
            reports = [r for r in reports if r.template_id == template_id]
        return reports

    def create_schedule(self, schedule: ReportSchedule) -> ReportSchedule:
        self._schedules[schedule.schedule_id] = schedule
        return schedule

    def get_schedules(self, enabled_only: bool = True) -> list[ReportSchedule]:
        schedules = list(self._schedules.values())
        if enabled_only:
            schedules = [s for s in schedules if s.enabled]
        return schedules

    def delete_template(self, template_id: str) -> bool:
        return self._templates.pop(template_id, None) is not None
