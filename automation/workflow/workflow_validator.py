"""Validation rules for workflow definitions."""

from __future__ import annotations

from typing import Any


class WorkflowValidator:
    """Checks workflow definitions for structural errors."""

    def validate(self, workflow: Any) -> list[str]:
        """Returns a list of issues (empty means the workflow is valid)."""
        issues: list[str] = []
        if not workflow.workflow_id:
            issues.append("workflow_id is required")
        if not workflow.name:
            issues.append("name is required")
        if not workflow.steps:
            issues.append("workflow has no steps")

        step_ids = [s.step_id for s in workflow.steps]
        if len(step_ids) != len(set(step_ids)):
            issues.append("duplicate step_ids detected")

        for step in workflow.steps:
            if not step.action:
                issues.append(f"step '{step.step_id}' has no action")
            if step.next_on_success and step.next_on_success not in step_ids:
                issues.append(
                    f"step '{step.step_id}' next_on_success points to "
                    f"unknown step '{step.next_on_success}'")
            if step.next_on_failure and step.next_on_failure not in step_ids:
                issues.append(
                    f"step '{step.step_id}' next_on_failure points to "
                    f"unknown step '{step.next_on_failure}'")
        return issues
