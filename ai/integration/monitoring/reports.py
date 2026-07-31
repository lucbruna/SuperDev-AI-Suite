"""
Integration Reports - Reporting
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Report:
    report_id: str
    name: str
    integration_id: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    format: str = "json"


class IntegrationReporter:
    def __init__(self):
        self.reports: list[Report] = []
        self.templates: dict[str, dict[str, Any]] = {}

    def generate_report(self, name: str, integration_id: str = "", data: dict[str, Any] = None) -> Report:
        report_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        report = Report(report_id=report_id, name=name, integration_id=integration_id, data=data or {})
        self.reports.append(report)
        return report

    def create_template(self, name: str, config: dict[str, Any]) -> None:
        self.templates[name] = config

    def get_template(self, name: str) -> dict[str, Any] | None:
        return self.templates.get(name)

    def get_report(self, report_id: str) -> Report | None:
        for r in self.reports:
            if r.report_id == report_id:
                return r
        return None

    def get_reports(self, integration_id: str = None) -> list[Report]:
        if integration_id:
            return [r for r in self.reports if r.integration_id == integration_id]
        return self.reports

    def get_summary(self, integration_id: str) -> dict[str, Any]:
        reports = [r for r in self.reports if r.integration_id == integration_id]
        return {
            "integration_id": integration_id,
            "total_reports": len(reports),
            "last_report": reports[-1].generated_at.isoformat() if reports else None,
        }

    def count(self) -> int:
        return len(self.reports)
