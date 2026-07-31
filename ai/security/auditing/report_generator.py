"""Compliance report generation."""

from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class ReportFormat(Enum):
    JSON = "json"
    SUMMARY = "summary"
    DETAILED = "detailed"


class ComplianceReport:
    def __init__(self, report_id: str, standard: str, title: str) -> None:
        self.report_id = report_id
        self.standard = standard
        self.title = title
        self.created_at = time.time()
        self.findings: list[dict[str, Any]] = []
        self.status = "draft"


class ReportGenerator:
    def __init__(self) -> None:
        self._reports: dict[str, ComplianceReport] = {}

    def create_report(self, standard: str, title: str) -> ComplianceReport:
        rid = str(uuid.uuid4())[:8]
        report = ComplianceReport(rid, standard, title)
        self._reports[rid] = report
        return report

    def add_finding(self, report_id: str, control: str, status: str, details: str = "") -> bool:
        report = self._reports.get(report_id)
        if report:
            report.findings.append({"control": control, "status": status, "details": details})
            return True
        return False

    def finalize(self, report_id: str) -> bool:
        report = self._reports.get(report_id)
        if report:
            report.status = "final"
            return True
        return False

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        report = self._reports.get(report_id)
        if report:
            return {
                "id": report.report_id,
                "standard": report.standard,
                "title": report.title,
                "status": report.status,
                "findings_count": len(report.findings),
                "findings": report.findings,
                "created_at": report.created_at,
            }
        return None

    def list_reports(self, standard: str = "") -> list[str]:
        if standard:
            return [r.report_id for r in self._reports.values() if r.standard == standard]
        return list(self._reports.keys())

    def summary(self, report_id: str) -> dict[str, Any]:
        report = self._reports.get(report_id)
        if not report:
            return {"error": "not_found"}
        passed = sum(1 for f in report.findings if f["status"] == "pass")
        failed = sum(1 for f in report.findings if f["status"] == "fail")
        return {
            "total": len(report.findings),
            "passed": passed,
            "failed": failed,
            "score": (passed / max(len(report.findings), 1)) * 100,
        }
