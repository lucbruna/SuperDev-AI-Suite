"""Reporter for quality analysis results."""

from typing import Any

from .models import IssueSeverity, QualityIssue, QualityMetric


class QualityReporter:
    """Generates quality reports and scores."""

    def __init__(self):
        self._severity_weights = {
            IssueSeverity.INFO: 1,
            IssueSeverity.WARNING: 3,
            IssueSeverity.ERROR: 7,
            IssueSeverity.CRITICAL: 10,
        }

    def compute_score(self, issues: list[QualityIssue], metrics: list[QualityMetric]) -> float:
        if not issues and not metrics:
            return 100.0

        total_weight = sum(self._severity_weights.get(i.severity, 1) for i in issues)
        penalty = min(50, total_weight * 2)
        score = max(0.0, 100.0 - penalty)
        return score

    def generate_summary(self, issues: list[QualityIssue]) -> dict[str, Any]:
        by_severity = {}
        by_category = {}
        for issue in issues:
            sev = issue.severity.value
            cat = issue.category.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_issues": len(issues),
            "by_severity": by_severity,
            "by_category": by_category,
            "has_critical": any(i.severity == IssueSeverity.CRITICAL for i in issues),
        }

    def format_report(self, issues: list[QualityIssue], metrics: list[QualityMetric]) -> str:
        score = self.compute_score(issues, metrics)
        lines = [
            "=== Quality Report ===",
            f"Score: {score:.1f}/100",
            f"Issues: {len(issues)}",
            "",
        ]
        for issue in issues[:10]:
            lines.append(f"  [{issue.severity.value}] L{issue.line_number}: {issue.message}")
        return "\n".join(lines)
