"""Converts analysis issues into actionable suggestions."""

from __future__ import annotations

from typing import Any

from automation.automation_protocols import new_id
from automation.optimization.optimizer_models import OptimizationSuggestion

_IMPACTS = {
    "timeout": "prevents hangs and runaway steps",
    "fallback": "handles failures automatically",
    "trigger": "enables autonomous execution",
    "split": "better observability and reuse",
    "automation": "removes manual work",
}


class OptimizerSuggester:
    """Builds OptimizationSuggestion objects from analyzer findings."""

    def suggest(self, workflow: Any,
                issues: list[dict[str, Any]]) -> list[OptimizationSuggestion]:
        suggestions: list[OptimizationSuggestion] = []
        for issue in issues:
            suggestions.append(OptimizationSuggestion(
                suggestion_id=new_id("opt"),
                target=issue.get("target", workflow.workflow_id),
                kind=issue["kind"],
                message=issue["message"],
                impact=_IMPACTS.get(issue["kind"], "")))
        return suggestions
