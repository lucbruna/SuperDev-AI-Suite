"""Protocol helpers / serialization for the Security Engine (Volume 16)."""

from __future__ import annotations

import json
from typing import Any

from .base import SecurityFinding, SecurityReport


def finding_to_dict(finding: SecurityFinding) -> dict[str, Any]:
    return finding.to_dict()


def report_to_dict(report: SecurityReport) -> dict[str, Any]:
    return report.to_dict()


def reports_to_json(reports: list[SecurityReport]) -> str:
    return json.dumps([r.to_dict() for r in reports], indent=2, default=str)


def dict_to_report(data: dict[str, Any]) -> SecurityReport:
    """Rebuild a SecurityReport from its serialized form (best effort)."""
    return SecurityReport(
        analyzer=data.get("analyzer", ""),
        target=data.get("target", ""),
        total_findings=data.get("total_findings", 0),
        scan_duration_ms=data.get("scan_duration_ms", 0.0),
        error=data.get("error", ""),
        timestamp=data.get("timestamp", ""),
        metadata=data.get("metadata", {}),
    )
