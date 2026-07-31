"""Final wiring tests for Volume 31 (Fase 6)."""

from __future__ import annotations

from agent_orchestration.agents import AgentEngine
from agent_orchestration.communication import CommunicationEngine
from agent_orchestration.decision import DecisionEngine
from agent_orchestration.evaluation import EvaluationEngine
from agent_orchestration.executor import ExecutorEngine
from agent_orchestration.learning import LearningEngine
from agent_orchestration.memory import MemoryEngine
from agent_orchestration.orchestrator_factory import build_orchestrator
from agent_orchestration.planner import PlannerEngine
from agent_orchestration.scheduling import SchedulingEngine


def test_factory_attaches_all_subsystems():
    engine = build_orchestrator()
    subsystems = engine.stats()["subsystems"]
    expected = {"agents_engine", "planner_engine", "executor_engine",
                "communication_engine", "memory_engine", "decision_engine",
                "evaluation_engine", "scheduling_engine", "learning_engine"}
    assert expected.issubset(set(subsystems))


def test_factory_wires_shared_events_metrics():
    engine = build_orchestrator()
    events = engine.events
    metrics = engine.metrics
    for name in ["agents_engine", "planner_engine", "executor_engine",
                 "communication_engine", "memory_engine", "decision_engine",
                 "evaluation_engine", "scheduling_engine", "learning_engine"]:
        subsystem = getattr(engine, name)
        assert subsystem is not None
        if hasattr(subsystem, "events"):
            assert subsystem.events is events
        if hasattr(subsystem, "metrics"):
            assert subsystem.metrics is metrics


def test_factory_shared_registry():
    engine = build_orchestrator()
    agent = engine.agents_engine.create("coding", "coder-1")
    assert engine.registry.get_agent(agent.agent_id) is not None
    planner = engine.planner_engine
    assert planner.registry is engine.registry


def test_end_to_end_flow():
    engine = build_orchestrator()
    engine.start()

    agents = engine.agents_engine.create_coding_team()
    assert len(agents) >= 1

    tasks = engine.planner_engine.plan(
        "criar sistema de login com autenticação segura e testes", agents)
    assert len(tasks) > 0

    for task in tasks:
        result = engine.executor_engine.execute(task)
        engine.memory_engine.record_experience(result)
        engine.metrics.snapshot()

    completed = [task for task in tasks
                 if task.status.value == "completed"]
    assert len(completed) > 0

    report = engine.evaluation_engine.evaluate(agents[0].agent_id)
    assert report.quality_score >= 0.0

    engine.communication_engine.send("coordinator", agents[0].agent_id,
                                     "bom trabalho")
    assert engine.communication_engine.bus.count() == 1

    engine.learning_engine.learn_from_feedback(
        agents[0].agent_id, "otimizar o login")
    stats = engine.stats()
    assert "manager" in stats
    assert len(stats["subsystems"]) == 9

    engine.stop()


def test_decision_and_scheduling_integration():
    engine = build_orchestrator()
    task = engine.create_task("deploy urgente")
    engine.decision_engine.decide_priority(task, 0.9)
    assert task.priority.value == "critical"
    engine.scheduling_engine.enqueue(task)
    assert engine.scheduling_engine.pending() == 1


def test_memory_and_learning_stats():
    engine = build_orchestrator()
    engine.memory_engine.remember("a1", "lang", "python")
    assert engine.memory_engine.recall("a1", "lang") == "python"
    stats = engine.learning_engine.stats()
    assert "metrics" in stats
