"""Tests for the validation engine (Phase G)."""
from __future__ import annotations

from modules.autonomous_developer.config import DeveloperConfig
from modules.autonomous_developer.config.constants import OP_CREATE, OP_MODIFY
from modules.autonomous_developer.core import DeveloperContext, DeveloperRegistry
from modules.autonomous_developer.core.models import FileChange, Task, TaskPlan
from modules.autonomous_developer.validation import (
    ValidationEngine,
    ValidationIssue,
    ValidationReport,
)


def make_context(tmp_path):
    return DeveloperContext(
        config=DeveloperConfig(project_root=tmp_path),
        registry=DeveloperRegistry(),
    )


def create_plan(goal="g", tasks=None):
    plan = TaskPlan(goal=goal)
    for task in tasks or []:
        plan.add_task(task)
    return plan


class TestValidationReport:
    def test_empty_report_is_valid(self):
        assert ValidationReport().valid

    def test_error_issue_invalidates(self):
        report = ValidationReport(issues=[ValidationIssue("x", "bad", "error")])
        assert not report.valid

    def test_warning_keeps_valid(self):
        report = ValidationReport(issues=[ValidationIssue("x", "warn", "warning")])
        assert report.valid

    def test_errors_and_warnings_split(self):
        issues = [
            ValidationIssue("a", "e", "error"),
            ValidationIssue("b", "w", "warning"),
        ]
        report = ValidationReport(issues=issues)
        assert [issue.path for issue in report.errors] == ["a"]
        assert [issue.path for issue in report.warnings] == ["b"]


class TestValidationEngineGoal:
    def test_empty_goal_invalid(self):
        assert not ValidationEngine().validate_goal("").valid

    def test_whitespace_goal_invalid(self):
        assert not ValidationEngine().validate_goal("   ").valid

    def test_valid_goal(self):
        report = ValidationEngine().validate_goal("Build a thing")
        assert report.valid
        assert report.issues == []


class TestValidationEngineFileChange:
    def test_valid_create(self):
        change = FileChange(path="app.py", content="x", operation=OP_CREATE)
        assert ValidationEngine().validate_file_change(change).valid

    def test_missing_path(self):
        change = FileChange(path="", content="x", operation=OP_CREATE)
        assert not ValidationEngine().validate_file_change(change).valid

    def test_create_without_content(self):
        change = FileChange(path="app.py", content=None, operation=OP_CREATE)
        assert not ValidationEngine().validate_file_change(change).valid

    def test_modify_without_old_content(self):
        change = FileChange(path="app.py", content="x", operation=OP_MODIFY)
        assert not ValidationEngine().validate_file_change(change).valid

    def test_unsupported_operation(self):
        change = FileChange(path="app.py", content="x", operation="explode")
        assert not ValidationEngine().validate_file_change(change).valid


class TestValidationEnginePlan:
    def test_none_plan_invalid(self):
        assert not ValidationEngine().validate_plan(None).valid

    def test_missing_task_title(self):
        plan = create_plan(tasks=[Task(title="")])
        assert not ValidationEngine().validate_plan(plan).valid

    def test_no_tasks_is_warning(self):
        report = ValidationEngine().validate_plan(create_plan())
        assert report.valid
        assert [issue.severity for issue in report.issues] == ["warning"]

    def test_too_many_files(self):
        files = [
            FileChange(path=f"f{i}.py", content="x", operation=OP_CREATE)
            for i in range(3)
        ]
        plan = create_plan(tasks=[Task(title="t", files=files)])
        assert not ValidationEngine(max_files_per_batch=2).validate_plan(plan).valid

    def test_task_file_changes_validated(self):
        bad = FileChange(path="", content=None, operation=OP_CREATE)
        plan = create_plan(tasks=[Task(title="t", files=[bad])])
        assert not ValidationEngine().validate_plan(plan).valid


class TestValidationEngineRun:
    def test_run_validates_plan_from_artifact(self, tmp_path):
        ctx = make_context(tmp_path)
        plan = create_plan(tasks=[Task(title="t", files=[FileChange(path="a.py", content="x", operation=OP_CREATE)])])
        ctx.set_artifact("plan", plan)
        assert ValidationEngine().run(ctx, "g").valid

    def test_run_validates_goal_without_plan(self, tmp_path):
        ctx = make_context(tmp_path)
        assert not ValidationEngine().run(ctx, "").valid

    def test_run_records_and_publishes(self, tmp_path):
        ctx = make_context(tmp_path)
        ValidationEngine().run(ctx, "ok goal")
        assert ctx.stats["validation_issues"] == 0
