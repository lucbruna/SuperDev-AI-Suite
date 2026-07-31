"""Core engine for quality analysis."""
from typing import List, Dict, Any, Optional
from .models import QualityReport, QualityIssue, QualityMetric, QualityRule
from .linter import Linter
from .formatter import Formatter
from .complexity_analyzer import ComplexityAnalyzer
from .quality_reporter import QualityReporter


class QualityEngine:
    """Central engine coordinating quality analysis operations."""

    def __init__(self):
        self.linter = Linter()
        self.formatter = Formatter()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.reporter = QualityReporter()
        self._rules: List[QualityRule] = []
        self._reports: List[QualityReport] = []

    def analyze_file(self, file_path: str, content: str) -> QualityReport:
        issues = self.linter.lint(content)
        metrics = self.complexity_analyzer.analyze(content)
        score = self.reporter.compute_score(issues, metrics)
        report = QualityReport(
            file_path=file_path,
            issues=issues,
            metrics=metrics,
            score=score,
        )
        self._reports.append(report)
        return report

    def add_rule(self, rule: QualityRule) -> None:
        self._rules.append(rule)

    def get_rules(self) -> List[QualityRule]:
        return list(self._rules)

    def get_reports(self) -> List[QualityReport]:
        return list(self._reports)

    def get_stats(self) -> Dict[str, Any]:
        total_issues = sum(r.issue_count for r in self._reports)
        return {
            "reports": len(self._reports),
            "rules": len(self._rules),
            "total_issues": total_issues,
            "avg_score": sum(r.score for r in self._reports) / len(self._reports) if self._reports else 0.0,
        }
