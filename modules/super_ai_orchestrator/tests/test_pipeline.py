"""Unit tests: pipeline (agents, llm, routing, planning, decision, execution)."""
from __future__ import annotations

from modules.super_ai_orchestrator.agents import AgentRegistry
from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.decision import DecisionEngine
from modules.super_ai_orchestrator.execution import TaskExecutor
from modules.super_ai_orchestrator.llm import LLMRegistry
from modules.super_ai_orchestrator.llm.registry import (
    ANALYSIS,
    CHEAP,
    CODING,
    LOCAL,
    REASONING,
)
from modules.super_ai_orchestrator.planning import Planner
from modules.super_ai_orchestrator.routing import Router

from modules.super_ai_orchestrator.tests.helpers import make_api, make_task


# ---------------------------------------------------------------------- #
# Agents
# ---------------------------------------------------------------------- #
def test_agent_registry_has_twelve_chiefs():
    registry = AgentRegistry()
    assert len(registry.all()) == 12
    assert "developer" in registry.names()
    assert "coordinator" in registry.names()


def test_agent_capabilities_and_tools():
    registry = AgentRegistry()
    developer = registry.get("developer")
    assert developer is not None
    assert developer.handles("develop")
    assert not developer.handles("deploy")
    assert "git" in developer.tools
    assert registry.capable_of("develop") == ("developer",)
    assert "developer" in registry.tool_users("git")


# ---------------------------------------------------------------------- #
# LLM registry
# ---------------------------------------------------------------------- #
def test_llm_registry_selects_highest_quality_by_default():
    registry = LLMRegistry()
    assert registry.select({CODING, REASONING}) == "claude"


def test_llm_registry_prefers_cheap_and_local():
    registry = LLMRegistry()
    # Zero-cost local providers win 'cheap'; ollama has CODING+REASONING and
    # cost 0.0, so it beats every paid provider.
    assert registry.select({CODING, REASONING}, prefer="cheap") == "ollama"
    assert registry.select({CODING, ANALYSIS}, prefer="local") == "ollama"
    assert registry.select({CODING, REASONING}, prefer="local") == "ollama"
    # Among paid providers, deepseek is the cheapest (requires CHEAP, which
    # excludes zero-cost local providers that lack the capability).
    assert registry.select({CODING, REASONING, ANALYSIS, CHEAP}, prefer="cheap") == "deepseek"


def test_llm_registry_no_supported_provider_raises():
    registry = LLMRegistry()
    try:
        registry.select({LOCAL, "vision-missing"})
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


# ---------------------------------------------------------------------- #
# Router
# ---------------------------------------------------------------------- #
def test_router_routes_kind_to_capable_owner():
    router = Router()
    owner, candidates = router.route("develop")
    assert owner == "developer"
    assert "developer" in candidates

    owner, candidates = router.route("analyze")
    assert owner == "architect"
    assert candidates == ["architect", "reviewer", "security", "infrastructure"]


def test_router_honors_capable_owner_hint_only():
    router = Router()
    assert router.route("develop", owner_hint="developer") == (
        "developer",
        ["developer"],
    )
    # Hint for an incapable agent is ignored.
    owner, _ = router.route("develop", owner_hint="reviewer")
    assert owner == "developer"


def test_router_unknown_kind_raises_when_required():
    router = Router()
    try:
        router.route("unknown-kind")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


# ---------------------------------------------------------------------- #
# Planner
# ---------------------------------------------------------------------- #
def test_planner_emits_kind_template():
    planner = Planner()
    plan = planner.plan(make_task(kind="develop"))
    actions = [step.action for step in plan]
    assert actions == ["inspect", "implement", "verify"]
    assert plan[0].index == 1
    assert "Implement the requested change" in plan[1].description


def test_planner_appends_scope_step_and_fallback():
    planner = Planner()
    scoped = planner.plan(make_task(kind="develop", payload={"scope": "auth"}))
    assert [s.action for s in scoped][-1] == "scope"

    unknown = planner.plan(make_task(kind="mystery"))
    assert [s.action for s in unknown] == ["prepare", "execute", "verify"]

    assert planner.summary(unknown) == "prepare -> execute -> verify"
    assert planner.to_dict(unknown) == [
        {"index": 1, "action": "prepare", "description": unknown[0].description},
        {"index": 2, "action": "execute", "description": unknown[1].description},
        {"index": 3, "action": "verify", "description": unknown[2].description},
    ]


# ---------------------------------------------------------------------- #
# DecisionEngine
# ---------------------------------------------------------------------- #
def test_decision_engine_decides_owner_llm_requires():
    api = make_api()
    kernel = api.kernel
    task = make_task(kind="develop")
    record = api.decision.decide(kernel, task)

    assert task.owner == "developer"
    assert task.llm == "claude"
    assert "git" in task.requires
    assert "llm" in task.requires
    assert record["task_seq"] == task.seq
    assert "decision.made" in [e.type for e in kernel.event_bus.log]
    assert "decided" in kernel.audit.kinds()


def test_decision_engine_merges_payload_tool_markers():
    api = make_api()
    task = make_task(kind="repair", payload={"docker": True, "requires": ["mcp"]})
    api.decision.decide(api.kernel, task)
    assert task.owner == "developer"
    assert {"docker", "mcp", "git", "llm"} <= set(task.requires)


def test_decision_engine_llm_prefer_hint():
    api = make_api()
    task = make_task(kind="analyze", payload={"llm_prefer": "cheap"})
    api.decision.decide(api.kernel, task)
    assert task.llm == "ollama"  # zero-cost local provider wins 'cheap'


# ---------------------------------------------------------------------- #
# TaskExecutor
# ---------------------------------------------------------------------- #
def test_executor_has_default_handler_for_every_kind():
    executor = TaskExecutor()
    for kind in ("develop", "repair", "monitor", "deploy", "coordinate", "agent"):
        assert executor.supports(kind)
    assert len(executor.kinds()) == 13


def test_executor_register_replace_unregister():
    executor = TaskExecutor()
    executor.register("develop", lambda context: {"custom": True})
    api = make_api()
    api.kernel.set_executor(executor.execute)
    task = api.kernel.submit(make_task())
    api.kernel.tick()
    assert task.status == TaskStatus.COMPLETED
    assert task.result == {"custom": True}

    assert executor.unregister("develop") is True
    assert executor.unregister("develop") is False
    try:
        executor.register("develop", "not-callable")  # type: ignore[arg-type]
        raise AssertionError("expected TypeError")
    except TypeError:
        pass


def test_executor_unknown_kind_raises():
    from modules.super_ai_orchestrator.core.context import OrchestrationContext

    executor = TaskExecutor()
    try:
        executor.execute(OrchestrationContext(task=make_task(kind="ghost")))
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
