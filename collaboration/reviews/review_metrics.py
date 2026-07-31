"""Review metrics and scoring."""

from __future__ import annotations

from typing import Any

from collaboration.reviews.review_findings import (count_by_severity,
                                                   severity_rank,
                                                   worst_severity)

PASS_THRESHOLD = 70.0


class ReviewMetrics:
    """Computes review scores and quality verdicts."""

    def score_from_criteria(self,
                            checklist: list[dict[str, Any]]) -> float:
        if not checklist:
            return 0.0
        passed = sum(1 for c in checklist if c.get("passed") is True)
        return round(passed / len(checklist) * 100.0, 1)

    def adjusted_score(self, score: float,
                       findings: list[dict[str, Any]]) -> float:
        """Penalizes the score for findings; critical findings zero it."""
        counts = count_by_severity(findings)
        if counts["critical"]:
            return 0.0
        penalty = counts["major"] * 10
        return round(max(0.0, score - penalty), 1)

    def verdict(self, score: float,
                findings: list[dict[str, Any]]) -> str:
        worst = worst_severity(findings)
        if worst == "critical":
            return "changes_requested"
        if score >= PASS_THRESHOLD and worst not in ("critical", "major"):
            return "approved"
        return "changes_requested"

    def summary(self, score: float,
                findings: list[dict[str, Any]]) -> dict[str, Any]:
        return {"score": score, "verdict": self.verdict(score, findings),
                "severities": count_by_severity(findings)}
