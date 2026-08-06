"""Unit tests: agents, workflows, plugins packages."""
from __future__ import annotations

from modules.ai_evolution_engine.agents.agent_registry import (
    AgentRegistry,
    EvolutionAgent,
)
from modules.ai_evolution_engine.agents.default_agents import build_default_agents
from modules.ai_evolution_engine.plugins.plugin_registry import (
    EvolutionPlugin,
    PluginRegistry,
)
from modules.ai_evolution_engine.tests.helpers import make_context
from modules.ai_evolution_engine.workflows.workflow_engine import (
    STANDARD_WORKFLOW,
    Workflow,
    WorkflowStep,
)


def test_agent_registry_register_and_run():
    registry = AgentRegistry()
    calls: list[str] = []

    def handler(ctx):
        calls.append("ran")
        return []

    registry.register(
        EvolutionAgent(name="alpha", role="test", handler=handler)
    )
    registry.run_all(make_context())
    assert calls == ["ran"]
    assert registry.names() == ["alpha"]


def test_agent_registry_disables_agent():
    registry = AgentRegistry()
    calls: list[str] = []

    def handler(ctx):
        calls.append("ran")
        return []

    registry.register(
        EvolutionAgent(name="off", role="test", enabled=False, handler=handler)
    )
    registry.run_all(make_context())
    assert calls == []


def test_default_agents_build():
    registry = build_default_agents()
    assert "analyst" in registry.names()
    # running should not raise
    registry.run_all(make_context())


def test_workflow_runs_steps_in_order():
    order: list[str] = []

    def make_step(name: str) -> WorkflowStep:
        def fn(ctx):
            order.append(name)
            return name

        return WorkflowStep(name=name, fn=fn)

    workflow = Workflow(name="test", steps=[make_step("a"), make_step("b")])
    outputs = workflow.run(make_context())
    assert outputs == ["a", "b"]
    assert order == ["a", "b"]


def test_standard_workflow_shape():
    assert STANDARD_WORKFLOW.name == "standard"
    assert [s.name for s in STANDARD_WORKFLOW.steps] == [
        "analyze",
        "recommend",
        "forecast",
        "govern",
        "plan",
        "report",
    ]


def test_plugin_registry_dispatch_by_phase():
    registry = PluginRegistry()
    captured: list[str] = []

    def hook(ctx):
        captured.append("analysis plugin")
        return None

    registry.register(
        EvolutionPlugin(name="auditor", phase="analyze", hook=hook)
    )
    registry.dispatch("analyze", make_context())
    assert captured == ["analysis plugin"]
    assert registry.dispatch("report", make_context()) == []


def test_plugin_registry_rejects_unknown_phase():
    registry = PluginRegistry()
    try:
        registry.register(EvolutionPlugin(name="bad", phase="nope"))
        raised = False
    except ValueError:
        raised = True
    assert raised
