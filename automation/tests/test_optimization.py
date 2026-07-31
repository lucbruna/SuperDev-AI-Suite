"""Tests for the optimization subsystem (Volume 20, Fase 7)."""

from __future__ import annotations

import pytest

from automation.automation_models import WorkflowDefinition, WorkflowStep
from automation.optimization.optimizer_analyzer import OptimizerAnalyzer
from automation.optimization.optimizer_engine import OptimizerEngine
from automation.optimization.optimizer_history import OptimizerHistory
from automation.optimization.optimizer_models import (
    OptimizationReport,
    OptimizationSuggestion,
)
from automation.optimization.optimizer_suggest import OptimizerSuggester


def _workflow(steps: list[WorkflowStep], triggers: list[str] | None = None):
    return WorkflowDefinition(workflow_id="wf-1", name="WF",
                              steps=steps, triggers=triggers or [])


class TestOptimizerModels:
    def test_suggestion_to_dict(self) -> None:
        suggestion = OptimizationSuggestion("opt-1", "s1", "timeout",
                                            "adicionar timeout")
        data = suggestion.to_dict()
        assert data["kind"] == "timeout"
        assert data["applied"] is False

    def test_report_to_dict(self) -> None:
        report = OptimizationReport("wf-1", [
            OptimizationSuggestion("opt-1", "wf-1", "trigger", "x")])
        data = report.to_dict()
        assert data["workflow_id"] == "wf-1"
        assert len(data["suggestions"]) == 1


class TestOptimizerAnalyzer:
    def test_flags_missing_timeout_and_fallback(self) -> None:
        workflow = _workflow([WorkflowStep("s1", "action.a"),
                              WorkflowStep("s2", "action.b",
                                           next_on_failure="s1")])
        issues = OptimizerAnalyzer().analyze(workflow)
        kinds = {issue["kind"] for issue in issues}
        assert "timeout" in kinds
        assert "fallback" in kinds  # s1 has no fallback
        assert "trigger" in kinds  # no triggers registered

    def test_no_issues_when_configured(self) -> None:
        workflow = _workflow(
            [WorkflowStep("s1", "action.a", timeout=10,
                          next_on_failure="s2"),
             WorkflowStep("s2", "action.b", timeout=10)],
            triggers=["tr-1"])
        assert OptimizerAnalyzer().analyze(workflow) == []

    def test_split_suggestion_for_many_steps(self) -> None:
        workflow = _workflow(
            [WorkflowStep(f"s{i}", f"action.{i}", timeout=5,
                          next_on_failure=f"s{i + 1}")
             for i in range(5)], triggers=["tr-1"])
        kinds = {issue["kind"] for issue in OptimizerAnalyzer().analyze(workflow)}
        assert "split" in kinds


class TestOptimizerSuggester:
    def test_suggestions_have_impact(self) -> None:
        workflow = _workflow([WorkflowStep("s1", "action.a")])
        issues = OptimizerAnalyzer().analyze(workflow)
        suggestions = OptimizerSuggester().suggest(workflow, issues)
        assert len(suggestions) >= 2
        assert all(s.impact for s in suggestions)
        assert all(s.kind for s in suggestions)


class TestOptimizerEngine:
    def test_analyze_returns_report(self) -> None:
        engine = OptimizerEngine()
        workflow = _workflow([WorkflowStep("s1", "action.a")])
        report = engine.analyze(workflow)
        assert isinstance(report, OptimizationReport)
        assert report.workflow_id == "wf-1"
        assert len(report.suggestions) >= 2
        assert engine.get_report("wf-1") is report
        assert len(engine.suggestion_history()) == len(report.suggestions)

    def test_apply_marks_suggestion(self) -> None:
        engine = OptimizerEngine()
        workflow = _workflow([WorkflowStep("s1", "action.a")])
        report = engine.analyze(workflow)
        suggestion_id = report.suggestions[0].suggestion_id
        assert engine.apply(suggestion_id) is True
        assert report.suggestions[0].applied is True
        assert engine.applied_count() == 1
        assert engine.apply("ghost") is False

    def test_suggest_automation_savings(self) -> None:
        """Exemplo real: relatório manual diário de 40min -> ~13h/mês."""
        engine = OptimizerEngine()
        suggestion = engine.suggest_automation("relatório diário",
                                               duration_minutes=40,
                                               times_per_month=20)
        assert suggestion.kind == "automation"
        assert "13.3h/mês" in suggestion.impact
        assert pytest.approx(float(suggestion.impact.split("~")[1]
                                   .split("h")[0])) == 13.3

    def test_user_example_autonomous_automation_suggestion(self) -> None:
        """IA sugere automação ao detectar relatório manual repetitivo."""
        engine = OptimizerEngine()
        suggestion = engine.suggest_automation("relatório de vendas",
                                               duration_minutes=40,
                                               times_per_month=20)
        assert "relatório de vendas" in suggestion.message
        assert "13.3h/mês" in suggestion.impact


class TestOptimizerHistory:
    def test_record_and_mark_applied(self) -> None:
        history = OptimizerHistory()
        report = OptimizationReport("wf-1", [
            OptimizationSuggestion("opt-1", "wf-1", "trigger", "x"),
            OptimizationSuggestion("opt-2", "wf-1", "timeout", "y")])
        history.record_suggestions(report)
        assert len(history.list()) == 2
        assert history.mark_applied("opt-1") is True
        assert history.applied_count() == 1
        assert history.mark_applied("ghost") is False
