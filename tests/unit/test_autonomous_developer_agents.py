"""Tests for the agent framework: developer agent and registry (Phase F)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.agents import (
    AgentRegistry,
    AgentResult,
    BaseAgent,
    DeveloperAgent,
)
from modules.autonomous_developer.config import DeveloperConfig
from modules.autonomous_developer.core import DeveloperContext, DeveloperRegistry
from modules.autonomous_developer.core.exceptions import ExecutionError
from modules.autonomous_developer.review import VERDICT_APPROVED

GOAL = "Create a demo application"
TASKS = [
    {
        "title": "Create app",
        "files": [{"path": "app.py", "content": "print('hi')"}],
    }
]


def make_context(tmp_path):
    return DeveloperContext(
        config=DeveloperConfig(project_root=tmp_path),
        registry=DeveloperRegistry(),
    )


class TestDeveloperAgent:
    def test_success_path_plans_generates_reviews(self, tmp_path):
        ctx = make_context(tmp_path)
        result = DeveloperAgent().run(ctx, GOAL, tasks=TASKS, dry_run=True)
        assert result.success
        assert result.agent == "developer"
        assert result.output["written"] == ["app.py"]
        assert result.artifacts["verdict"] == VERDICT_APPROVED
        assert result.artifacts["files"] == ["app.py"]
        assert result.duration_seconds >= 0

    def test_stores_plan_artifact(self, tmp_path):
        ctx = make_context(tmp_path)
        result = DeveloperAgent().run(ctx, GOAL, tasks=TASKS, dry_run=True)
        plan = ctx.get_artifact("plan")
        assert plan is not None
        assert plan.plan_id == result.artifacts["plan_id"]

    def test_writes_files_when_not_dry_run(self, tmp_path):
        ctx = make_context(tmp_path)
        result = DeveloperAgent().run(ctx, GOAL, tasks=TASKS, dry_run=False)
        assert result.success
        assert (tmp_path / "app.py").exists()

    def test_error_is_captured_on_result(self, tmp_path):
        class BoomPlanner:
            def run(self, ctx, goal, **kwargs):
                raise ExecutionError("boom")

        ctx = make_context(tmp_path)
        result = DeveloperAgent().run(ctx, "x", planner=BoomPlanner())
        assert not result.success
        assert "boom" in result.error
        assert result.agent == "developer"
        assert result.duration_seconds >= 0

    def test_empty_goal_returns_error_result(self, tmp_path):
        ctx = make_context(tmp_path)
        result = DeveloperAgent().run(ctx, "")
        assert not result.success
        assert result.error


class TestAgentRegistry:
    def test_register_get_names(self):
        registry = AgentRegistry()
        agent = DeveloperAgent()
        registry.register(agent)
        assert registry.names() == ["developer"]
        assert registry.get("developer") is agent

    def test_run_dispatches(self, tmp_path):
        ctx = make_context(tmp_path)
        registry = AgentRegistry()
        registry.register(DeveloperAgent())
        result = registry.run("developer", ctx, GOAL, tasks=TASKS, dry_run=True)
        assert result.success
        assert result.agent == "developer"

    def test_unknown_agent_raises(self, tmp_path):
        with pytest.raises(ExecutionError):
            AgentRegistry().run("nope", make_context(tmp_path), "x")

    def test_run_wraps_exceptions(self, tmp_path):
        class BoomAgent(BaseAgent):
            name = "boom"

            def run(self, ctx, goal, **kwargs):
                raise RuntimeError("kaboom")

        ctx = make_context(tmp_path)
        registry = AgentRegistry()
        registry.register(BoomAgent())
        result = registry.run("boom", ctx, "x")
        assert not result.success
        assert "kaboom" in result.error
        assert result.duration_seconds >= 0

    def test_agent_result_success_property(self):
        assert AgentResult().success
        assert not AgentResult(error="nope").success
