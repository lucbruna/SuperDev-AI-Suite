"""Cost accounting and per-phase trace for the full loop."""
from __future__ import annotations

from pathlib import Path

from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.costs import CostTracker, estimate_cost
from modules.autonomous_developer.core.exceptions import DeveloperError
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.core.runtime import DeveloperRuntime
from modules.autonomous_developer.generator.generator import GenerationResult
from modules.autonomous_developer.planner.project_planner import ProjectPlanner


class StubPlanner:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        plan = ProjectPlanner().plan(goal, tasks=[f"Fix {goal}"])
        ctx.record_usage("plan", 1_000, 200)
        return plan


class StubGenerator:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        return GenerationResult(written=[])


class FailingValidator:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        raise DeveloperError("tests failed")


def _runtime(tmp_path: Path, validator=None) -> DeveloperRuntime:
    registry = DeveloperRegistry()
    registry.register("planner", "default", StubPlanner())
    registry.register("generator", "default", StubGenerator())
    registry.register("validator", "default", validator or FailingValidator())
    config = DeveloperConfig(
        project_root=str(tmp_path),
        run_tests=True,
        run_review=True,
        create_pr=False,
    )
    return DeveloperRuntime(config=config, registry=registry)


class TestEstimateCost:
    def test_known_rates(self):
        # 1000 input * 0.00015 + 1000 output * 0.00060, per 1k.
        assert estimate_cost(1_000, 1_000) == 0.00075
        assert estimate_cost(0, 0) == 0.0
        assert estimate_cost(2_000, 500) == 0.00060


class TestCostTracker:
    def test_totals(self):
        tracker = CostTracker()
        tracker.record("plan", 1_000, 200)
        tracker.record("review", 500, 100)
        totals = tracker.totals()
        assert totals["calls"] == 2
        assert totals["prompt_tokens"] == 1_500
        assert totals["completion_tokens"] == 300
        assert totals["cost_usd"] == round(estimate_cost(1_500, 300), 6)
        assert len(tracker.entries) == 2
        assert tracker.entries[0]["phase"] == "plan"

    def test_reset(self):
        tracker = CostTracker()
        tracker.record("plan", 10, 10)
        tracker.reset()
        assert tracker.totals()["calls"] == 0


class TestLoopTrace:
    def test_success_phase_trace_and_cost(self, tmp_path: Path):
        runtime = _runtime(tmp_path, validator=StubGenerator())

        ctx = runtime.execute("sum", phases=("plan", "implement", "test"))
        assert ctx.state.to_dict()["state"] == "ready"
        assert [e["phase"] for e in ctx.trace] == ["plan", "implement", "test"]
        assert all(e["status"] == "completed" for e in ctx.trace)
        assert all(e["elapsed_seconds"] >= 0 for e in ctx.trace)

        # Usage recorded by the stub planner surfaced in stats + status.
        assert ctx.stats["llm_calls"] == 1
        assert ctx.stats["llm_prompt_tokens"] == 1_000
        assert ctx.stats["llm_cost_usd"] == round(estimate_cost(1_000, 200), 6)
        status = runtime.status()
        assert status["cost"]["calls"] == 1
        assert status["cost"]["cost_usd"] == ctx.stats["llm_cost_usd"]
        assert len(status["trace"]) == 3

    def test_failure_records_failed_phase(self, tmp_path: Path):
        runtime = _runtime(tmp_path)
        ctx = runtime.execute("sum")
        failed = ctx.trace[-1]
        assert failed["phase"] == "test"
        assert failed["status"] == "failed"
        assert failed["error"] == "tests failed"
        assert failed["elapsed_seconds"] >= 0

    def test_reset_clears_trace_and_usage(self, tmp_path: Path):
        runtime = _runtime(tmp_path, validator=StubGenerator())
        runtime.execute("sum", phases=("plan",))
        assert runtime.status()["cost"]["calls"] == 1
        runtime.reset()
        status = runtime.status()
        assert status["trace"] == []
        assert status["cost"]["calls"] == 0
        assert "llm_calls" not in status["stats"]
