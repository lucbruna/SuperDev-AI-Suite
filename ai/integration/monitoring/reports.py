"""
Integration Reports - Reporting
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class Report:
    report_id: str
    name: str
    integration_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    format: str = "json"


class IntegrationReporter:
    def __init__(self):
        self.reports: List[Report] = []
        self.templates: Dict[str, Dict[str, Any]] = {}

    def generate_report(self, name: str, integration_id: str = "", data: Dict[str, Any] = None) -> Report:
        report_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        report = Report(report_id=report_id, name=name, integration_id=integration_id, data=data or {})
        self.reports.append(report)
        return report

    def create_template(self, name: str, config: Dict[str, Any]) -> None:
        self.templates[name] = config

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        return self.templates.get(name)

    def get_report(self, report_id: str) -> Optional[Report]:
        for r in self.reports:
            if r.report_id == report_id:
                return r
        return None

    def get_reports(self, integration_id: str = None) -> List[Report]:
        if integration_id:
            return [r for r in self.reports if r.integration_id == integration_id]
        return self.reports

    def get_summary(self, integration_id: str) -> Dict[str, Any]:
        reports = [r for r in self.reports if r.integration_id == integration_id]
        return {"integration_id": integration_id, "total_reports": len(reports), "last_report": reports[-1].generated_at.isoformat() if reports else None}

    def count(self) -> int:
        return len(self.reports)
