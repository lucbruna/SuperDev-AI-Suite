"""Report generator for evaluation results."""

from __future__ import annotations

import time
from typing import Any


class ReportGenerator:
    """Generates structured evaluation reports."""

    def __init__(self) -> None:
        self._reports: list[dict[str, Any]] = []

    def generate(self, data: dict[str, Any]) -> dict[str, Any]:
        report = {
            "report_id": f"report_{len(self._reports) + 1}",
            "timestamp": time.time(),
            "summary": self._summarize(data),
            "details": data,
            "recommendations": self._recommend(data),
        }
        self._reports.append(report)
        return report

    def _summarize(self, data: dict[str, Any]) -> dict[str, Any]:
        overall = data.get("overall", data.get("score", 0.5))
        return {
            "overall_score": overall,
            "status": "pass" if float(overall) >= 0.6 else "fail",
            "key_findings": self._extract_findings(data),
        }

    def _extract_findings(self, data: dict[str, Any]) -> list[str]:
        findings: list[str] = []
        if "performance" in data:
            perf = data["performance"]
            if isinstance(perf, dict):
                score = perf.get("score", 0.5)
                findings.append(f"Performance score: {score}")
        if "quality" in data:
            q = data["quality"]
            if isinstance(q, dict):
                findings.append(f"Quality score: {q.get('score', 0.5)}")
        if not findings:
            findings.append("Report generated with available data")
        return findings

    def _recommend(self, data: dict[str, Any]) -> list[str]:
        recs: list[str] = []
        overall = float(data.get("overall", data.get("score", 0.5)))
        if overall < 0.5:
            recs.append("Consider additional training or configuration changes")
        if overall < 0.7:
            recs.append("Review recent performance for improvement areas")
        if overall >= 0.8:
            recs.append("Agent performing well - maintain current configuration")
        return recs

    def get_reports(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._reports[-limit:]
