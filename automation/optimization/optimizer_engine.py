"""Optimizer engine: facade for the optimization subsystem."""

from __future__ import annotations

from typing import Any

from automation.automation_protocols import new_id
from automation.optimization.optimizer_analyzer import OptimizerAnalyzer
from automation.optimization.optimizer_history import OptimizerHistory
from automation.optimization.optimizer_models import (
    OptimizationReport,
    OptimizationSuggestion,
)
from automation.optimization.optimizer_suggest import OptimizerSuggester


class OptimizerEngine:
    """Analyzes workflows and suggests concrete improvements."""

    def __init__(self, analyzer: OptimizerAnalyzer | None = None,
                 suggester: OptimizerSuggester | None = None,
                 history: OptimizerHistory | None = None) -> None:
        self.analyzer = analyzer or OptimizerAnalyzer()
        self.suggester = suggester or OptimizerSuggester()
        self.history = history or OptimizerHistory()
        self._reports: dict[str, OptimizationReport] = {}

    def analyze(self, workflow: Any) -> OptimizationReport:
        issues = self.analyzer.analyze(workflow)
        suggestions = self.suggester.suggest(workflow, issues)
        report = OptimizationReport(workflow.workflow_id, suggestions)
        self._reports[workflow.workflow_id] = report
        self.history.record_suggestions(report)
        return report

    def get_report(self, workflow_id: str) -> OptimizationReport | None:
        return self._reports.get(workflow_id)

    def apply(self, suggestion_id: str) -> bool:
        for report in self._reports.values():
            for suggestion in report.suggestions:
                if suggestion.suggestion_id == suggestion_id:
                    suggestion.applied = True
                    self.history.mark_applied(suggestion_id)
                    return True
        return False

    def suggestion_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.history.list(limit)

    def applied_count(self) -> int:
        return self.history.applied_count()

    def suggest_automation(self, task: str, duration_minutes: float,
                           times_per_month: int) -> OptimizationSuggestion:
        """Sugere automação para trabalho manual repetitivo.

        Ex.: relatório manual diário de 40min x 20 dias = ~13h/mês.
        """
        savings_hours = duration_minutes * times_per_month / 60.0
        suggestion = OptimizationSuggestion(
            suggestion_id=new_id("opt"),
            target=task,
            kind="automation",
            message=f"automatizar '{task}' (execução manual repetitiva)",
            impact=f"economia de ~{savings_hours:.1f}h/mês")
        return suggestion
