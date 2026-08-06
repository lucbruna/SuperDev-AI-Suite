"""Deterministic plan, goal and file-change validation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from modules.autonomous_developer.config.constants import OP_CREATE, OP_DELETE, OP_MODIFY
from modules.autonomous_developer.core.models import FileChange, TaskPlan

if TYPE_CHECKING:
    from modules.autonomous_developer.core.context import DeveloperContext

__all__ = ["ValidationEngine", "ValidationIssue", "ValidationReport"]

_ALLOWED_OPERATIONS = frozenset({OP_CREATE, OP_MODIFY, OP_DELETE})


@dataclass(slots=True)
class ValidationIssue:
    """A single finding: an error blocks the plan, a warning does not."""

    path: str
    message: str
    severity: str  # "error" | "warning"


@dataclass(slots=True)
class ValidationReport:
    """Collection of issues; valid unless an error is present."""

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    @property
    def errors(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.severity == "warning"]


class ValidationEngine:
    """Validates goals, file changes and plans with plain rules."""

    def __init__(self, max_files_per_batch: int = 100) -> None:
        self.max_files_per_batch = max_files_per_batch

    def validate_goal(self, goal: str) -> ValidationReport:
        issues: list[ValidationIssue] = []
        if not isinstance(goal, str) or not goal.strip():
            issues.append(
                ValidationIssue("goal", "Goal must be a non-empty string", "error")
            )
        return ValidationReport(issues=issues)

    def validate_file_change(self, change: FileChange) -> ValidationReport:
        issues: list[ValidationIssue] = []
        if not change.path or not change.path.strip():
            issues.append(ValidationIssue("path", "File change requires a path", "error"))
        if change.operation not in _ALLOWED_OPERATIONS:
            issues.append(
                ValidationIssue(
                    change.path, f"Unsupported operation: {change.operation!r}", "error"
                )
            )
        if change.operation == OP_CREATE and change.content is None:
            issues.append(
                ValidationIssue(change.path, "Create requires content", "error")
            )
        if change.operation == OP_MODIFY and change.old_content is None:
            issues.append(
                ValidationIssue(change.path, "Modify requires old_content", "error")
            )
        return ValidationReport(issues=issues)

    def validate_plan(self, plan: TaskPlan | None) -> ValidationReport:
        if plan is None:
            return ValidationReport(
                issues=[ValidationIssue("plan", "Plan is required", "error")]
            )
        issues: list[ValidationIssue] = []
        if not plan.tasks:
            issues.append(ValidationIssue("plan", "Plan contains no tasks", "warning"))
        total_files = sum(len(task.files) for task in plan.tasks)
        if total_files > self.max_files_per_batch:
            issues.append(
                ValidationIssue(
                    "plan",
                    f"Too many files ({total_files} > {self.max_files_per_batch})",
                    "error",
                )
            )
        for task in plan.tasks:
            if not task.title or not task.title.strip():
                issues.append(
                    ValidationIssue(task.task_id, "Task requires a title", "error")
                )
            for change in task.files:
                issues.extend(self.validate_file_change(change).issues)
        return ValidationReport(issues=issues)

    def run(
        self, ctx: DeveloperContext, goal: str, **kwargs: Any
    ) -> ValidationReport:
        """Validate the plan artifact when present, otherwise the goal."""
        plan = kwargs.get("plan")
        if plan is None:
            plan = ctx.get_artifact("plan")
        report = (
            self.validate_plan(plan) if plan is not None else self.validate_goal(goal)
        )
        ctx.record("validation_issues", len(report.issues))
        ctx.publish(
            "validation.done",
            {"valid": report.valid, "issue_count": len(report.issues)},
        )
        return report
