"""Review findings."""

from __future__ import annotations

from typing import Any

SEVERITY_ORDER = {"critical": 4, "major": 3, "minor": 2, "info": 1}


def make_finding(severity: str, message: str,
                 location: str = "") -> dict[str, Any]:
    """Creates a finding with normalized severity."""
    severity = severity if severity in SEVERITY_ORDER else "info"
    return {"severity": severity, "message": message,
            "location": location}


def severity_rank(finding: dict[str, Any]) -> int:
    return SEVERITY_ORDER.get(finding.get("severity", "info"), 1)


def worst_severity(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "info"
    return max((severity_rank(f), f.get("severity", "info"))
               for f in findings)[1]


def count_by_severity(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts = {s: 0 for s in SEVERITY_ORDER}
    for finding in findings:
        severity = finding.get("severity", "info")
        if severity in counts:
            counts[severity] += 1
    return counts


def sort_findings(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(findings, key=severity_rank, reverse=True)
