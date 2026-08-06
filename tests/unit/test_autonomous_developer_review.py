"""Unit tests for the Autonomous Developer code reviewer (Phase E)."""
from __future__ import annotations

import pytest

import modules.autonomous_developer.review as _review
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.config.generator_config import GeneratorConfig
from modules.autonomous_developer.core.context import DeveloperContext
from modules.autonomous_developer.core.exceptions import GenerationError
from modules.autonomous_developer.core.models import FileChange
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.review import (
    VERDICT_APPROVED,
    VERDICT_CHANGES_REQUESTED,
    VERDICT_REJECTED,
    CodeReviewer,
)


class TestReviewChanges:
    def test_empty_changes_request_changes(self) -> None:
        verdict = CodeReviewer().review_changes([])
        assert verdict.verdict == VERDICT_CHANGES_REQUESTED
        assert verdict.issues == ["No changes to review"]

    def test_clean_change_approved(self, tmp_path) -> None:
        verdict = CodeReviewer().review_changes(
            [FileChange(path="app.py", content="x = 1")],
            project_root=tmp_path,
        )
        assert verdict.verdict == VERDICT_APPROVED
        assert verdict.issues == []
        assert verdict.comments == "All checks passed."

    def test_secret_content_rejected(self, tmp_path) -> None:
        verdict = CodeReviewer().review_changes(
            [FileChange(path="app.py", content="api_key = 'abc123'")],
            project_root=tmp_path,
        )
        assert verdict.verdict == VERDICT_REJECTED
        assert any("Secret-like content" in issue for issue in verdict.issues)

    def test_path_escape_rejected(self, tmp_path) -> None:
        verdict = CodeReviewer().review_changes(
            [FileChange(path="../escape.txt", content="x")],
            project_root=tmp_path,
        )
        assert verdict.verdict == VERDICT_REJECTED
        assert any("Path escapes project root" in issue for issue in verdict.issues)

    def test_blocked_pattern_rejected(self, tmp_path) -> None:
        verdict = CodeReviewer().review_changes(
            [FileChange(path=".env", content="x")],
            project_root=tmp_path,
        )
        assert verdict.verdict == VERDICT_REJECTED

    def test_oversized_change_requests_changes(self, tmp_path) -> None:
        config = GeneratorConfig(max_file_size_bytes=10)
        verdict = CodeReviewer(config).review_changes(
            [FileChange(path="app.py", content="x" * 20)],
            project_root=tmp_path,
        )
        assert verdict.verdict == VERDICT_CHANGES_REQUESTED
        assert any("File too large" in issue for issue in verdict.issues)

    def test_create_without_content_requests_changes(self, tmp_path) -> None:
        verdict = CodeReviewer().review_changes(
            [FileChange(path="app.py")],
            project_root=tmp_path,
        )
        assert verdict.verdict == VERDICT_CHANGES_REQUESTED
        assert any("Create without content" in issue for issue in verdict.issues)

    def test_dict_specs_accepted(self, tmp_path) -> None:
        verdict = CodeReviewer().review_changes(
            [{"path": "app.py", "content": "x = 1"}],
            project_root=tmp_path,
        )
        assert verdict.verdict == VERDICT_APPROVED

    def test_task_id_carried(self, tmp_path) -> None:
        verdict = CodeReviewer().review_changes(
            [FileChange(path="app.py", content="x = 1")],
            task_id="task-1",
            project_root=tmp_path,
        )
        assert verdict.task_id == "task-1"


class TestRun:
    def _context(self, tmp_path) -> DeveloperContext:
        config = DeveloperConfig(project_root=str(tmp_path))
        return DeveloperContext(config=config, registry=DeveloperRegistry())

    def test_run_reviews_kwarg_changes(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        verdict = CodeReviewer().run(
            ctx, "goal", changes=[{"path": "app.py", "content": "x = 1"}]
        )
        assert verdict.verdict == VERDICT_APPROVED
        assert ctx.stats["review_verdict"] == VERDICT_APPROVED
        assert ctx.stats["review_issues"] == 0
        events = [e.type for e in ctx.bus.history(event_type="review.completed")]
        assert events == ["review.completed"]

    def test_run_reviews_plan_artifact(self, tmp_path) -> None:
        from modules.autonomous_developer.planner import ProjectPlanner

        ctx = self._context(tmp_path)
        plan = ProjectPlanner().plan(
            "goal",
            tasks=[
                {
                    "title": "Create app",
                    "files": [{"path": "app.py", "content": "x = 1", "reason": "core"}],
                }
            ],
        )
        ctx.set_artifact("plan", plan)
        verdict = CodeReviewer().run(ctx, "goal")
        assert verdict.verdict == VERDICT_APPROVED

    def test_run_rejected_raises(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        with pytest.raises(GenerationError, match="Rejected:"):
            CodeReviewer().run(
                ctx, "goal", changes=[{"path": ".env", "content": "x"}]
            )
        assert ctx.stats["review_verdict"] == VERDICT_REJECTED

    def test_run_no_changes_requests_changes(self, tmp_path) -> None:
        ctx = self._context(tmp_path)
        verdict = CodeReviewer().run(ctx, "goal")
        assert verdict.verdict == VERDICT_CHANGES_REQUESTED
