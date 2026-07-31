"""Manager for quality configurations and history."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import QualityReport, QualityRule, QualityMetric


class QualityManager:
    """Manages quality analysis configurations and history."""

    def __init__(self):
        self._rules: List[QualityRule] = []
        self._reports: List[QualityReport] = []
        self._history: List[Dict[str, Any]] = []

    def add_rule(self, rule: QualityRule) -> None:
        self._rules.append(rule)

    def get_rules(self) -> List[QualityRule]:
        return list(self._rules)

    def enable_rule(self, rule_id: str) -> bool:
        for rule in self._rules:
            if rule.rule_id == rule_id:
                rule.enabled = True
                return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        for rule in self._rules:
            if rule.rule_id == rule_id:
                rule.enabled = False
                return True
        return False

    def add_report(self, report: QualityReport) -> None:
        self._reports.append(report)
        self._history.append({
            "report_id": report.report_id,
            "score": report.score,
            "issues": report.issue_count,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_reports(self) -> List[QualityReport]:
        return list(self._reports)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "rules": len(self._rules),
            "reports": len(self._reports),
            "avg_score": sum(r.score for r in self._reports) / len(self._reports) if self._reports else 0.0,
        }
