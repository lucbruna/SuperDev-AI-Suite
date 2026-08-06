"""LLMPlanner: live-LLM planning with deterministic fallback."""
from __future__ import annotations

import json
from pathlib import Path

import httpx

from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.config.llm_config import LLMConfig
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.core.runtime import DeveloperRuntime, build_runtime
from modules.autonomous_developer.generator.generator import GenerationResult
from modules.autonomous_developer.llm.client import LLMClient
from modules.autonomous_developer.memory.lessons import Lesson
from modules.autonomous_developer.planner.llm_planner import LLMPlanner
from modules.autonomous_developer.planner.project_planner import ProjectPlanner
from modules.autonomous_developer.tests.helpers import make_context

_PLAN_JSON = {
    "goal": "Fix add() so it returns the sum",
    "tasks": [
        {
            "title": "fix add",
            "description": "make add return the sum",
            "priority": "high",
            "risk": "medium",
            "files": [{"path": "calc.py", "content": "def add(a, b):\n    return a + b\n"}],
        }
    ],
}


def _failing_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("provider unreachable", request=request)


class TestLLMPlanner:
    def test_deterministic_when_llm_disabled(self, tmp_path: Path):
        # Default config: LLM disabled → identical to ProjectPlanner output.
        ctx = make_context(tmp_path)
        planner = LLMPlanner()
        plan = planner.run(ctx, "Fix add() so it returns the sum")
        expected = ProjectPlanner().plan("Fix add() so it returns the sum")
        assert [t.title for t in plan.tasks] == [t.title for t in expected.tasks]
        assert "llm_calls" not in ctx.stats  # no usage recorded

    def test_mock_llm_drives_plan_and_usage(self, tmp_path: Path):
        ctx = make_context(tmp_path)
        planner = LLMPlanner(
            client=LLMClient(mock_response=json.dumps(_PLAN_JSON))
        )
        plan = planner.run(ctx, "Fix add() so it returns the sum")
        assert plan.tasks[0].title == "fix add"
        assert plan.tasks[0].risk == "medium"
        assert plan.tasks[0].files[0].path == "calc.py"
        # Usage surfaced through the context cost tracker.
        assert ctx.stats["llm_calls"] == 1
        assert ctx.stats["llm_cost_usd"] > 0
        assert ctx.usage.totals()["calls"] == 1

    def test_fallback_on_invalid_json(self, tmp_path: Path):
        ctx = make_context(tmp_path)
        planner = LLMPlanner(client=LLMClient(mock_response="not json at all"))
        plan = planner.run(ctx, "Fix add() so it returns the sum")
        assert len(plan.tasks) == 1  # deterministic decomposition
        assert "llm_calls" not in ctx.stats

    def test_fallback_on_llm_error(self, tmp_path: Path):
        ctx = make_context(tmp_path)
        client = LLMClient(
            config=LLMConfig(
                enabled=True,
                provider="openai",
                openai_api_key="k",
                fallback_to_echo=False,
            ),
            transport=httpx.MockTransport(_failing_handler),
        )
        planner = LLMPlanner(client=client)
        plan = planner.run(ctx, "Fix add() so it returns the sum")
        assert len(plan.tasks) == 1  # deterministic fallback, no crash
        assert "llm_calls" not in ctx.stats

    def test_lessons_injected_into_prompt(self, tmp_path: Path):
        ctx = make_context(tmp_path)
        ctx.lessons.add(Lesson(phase="test", goal="Fix add() so it returns the sum",
                               error="tests failed"))
        seen: dict[str, str] = {}

        class _SpyClient(LLMClient):
            def complete(self, prompt, *, max_tokens=None):
                seen["prompt"] = prompt
                return super().complete(prompt, max_tokens=max_tokens)

        planner = LLMPlanner(client=_SpyClient(mock_response=json.dumps(_PLAN_JSON)))
        planner.run(ctx, "Fix add() so it returns the sum")
        assert "Previous failures to avoid" in seen["prompt"]
        assert "tests failed" in seen["prompt"]

    def test_explicit_tasks_skip_llm(self, tmp_path: Path):
        ctx = make_context(tmp_path)
        planner = LLMPlanner(
            client=LLMClient(mock_response=json.dumps(_PLAN_JSON))
        )
        plan = planner.run(
            ctx, "Fix add()", tasks=["manual task one", "manual task two"]
        )
        assert [t.title for t in plan.tasks] == ["manual task one", "manual task two"]
        assert "llm_calls" not in ctx.stats  # explicit specs win, no LLM call


class TestDefaultRegistry:
    def test_default_planner_is_llm_planner(self):
        runtime = build_runtime()
        planner = runtime.registry.get("planner", "default")
        assert isinstance(planner, LLMPlanner)

    def test_loop_with_mock_llm_records_cost(self, tmp_path: Path):
        registry = DeveloperRegistry()
        registry.register("planner", "default",
                          LLMPlanner(client=LLMClient(mock_response=json.dumps(_PLAN_JSON))))
        registry.register("generator", "default", _StubGenerator())
        registry.register("validator", "default", _StubValidator())
        registry.register("reviewer", "default", _StubReviewer())
        registry.register("executor", "default", _StubExecutor())
        config = DeveloperConfig(
            project_root=str(tmp_path),
            run_tests=False,
            run_review=False,
            create_pr=False,
        )
        runtime = DeveloperRuntime(config=config, registry=registry)
        ctx = runtime.execute("Fix add() so it returns the sum")
        assert ctx.state.to_dict()["state"] == "ready"
        plan = ctx.get_artifact("plan")
        assert plan.tasks[0].title == "fix add"
        assert ctx.stats["llm_calls"] == 1


class _StubGenerator:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        return GenerationResult(written=[])


class _StubValidator:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        return {"status": "skipped", "passed": False}


class _StubReviewer:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        return {"approved": True, "issues": []}


class _StubExecutor:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        return {"status": "skipped"}
