"""Detects improvement opportunities in workflows."""

from __future__ import annotations

from typing import Any


class OptimizerAnalyzer:
    """Rule-based analysis of a workflow definition."""

    def analyze(self, workflow: Any) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []
        last_step_id = workflow.steps[-1].step_id if workflow.steps else None
        for step in workflow.steps:
            if step.timeout is None:
                issues.append({
                    "kind": "timeout",
                    "target": step.step_id,
                    "message": f"step '{step.step_id}' has no timeout",
                })
            if step.next_on_failure is None and step.step_id != last_step_id:
                issues.append({
                    "kind": "fallback",
                    "target": step.step_id,
                    "message": f"step '{step.step_id}' has no failure fallback",
                })
        if not workflow.triggers:
            issues.append({
                "kind": "trigger",
                "target": workflow.workflow_id,
                "message": f"workflow '{workflow.workflow_id}' has no triggers",
            })
        if len(workflow.steps) >= 5:
            issues.append({
                "kind": "split",
                "target": workflow.workflow_id,
                "message": "workflow has many steps; consider a pipeline",
            })
        return issues
