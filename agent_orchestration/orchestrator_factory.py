"""Factory for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.agents import AgentEngine
from agent_orchestration.communication import CommunicationEngine
from agent_orchestration.decision import DecisionEngine
from agent_orchestration.evaluation import EvaluationEngine
from agent_orchestration.executor import ExecutorEngine
from agent_orchestration.learning import LearningEngine
from agent_orchestration.memory import MemoryEngine
from agent_orchestration.orchestrator_config import OrchestratorConfig
from agent_orchestration.orchestrator_context import OrchestratorContext
from agent_orchestration.orchestrator_engine import OrchestratorEngine
from agent_orchestration.orchestrator_events import OrchestratorEvents
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_registry import OrchestratorRegistry
from agent_orchestration.orchestrator_runtime import OrchestratorRuntime
from agent_orchestration.orchestrator_security import OrchestratorSecurity
from agent_orchestration.planner import PlannerEngine
from agent_orchestration.scheduling import SchedulingEngine


def build_orchestrator(
        config: dict[str, Any] | None = None) -> OrchestratorEngine:
    """Builds a fully wired OrchestratorEngine with all subsystems."""
    engine = OrchestratorEngine(
        config=OrchestratorConfig(**(config or {})),
        events=OrchestratorEvents(),
        metrics=OrchestratorMetrics(),
        registry=OrchestratorRegistry(),
        security=OrchestratorSecurity(),
        context=OrchestratorContext(),
        runtime=OrchestratorRuntime())

    events = engine.events
    metrics = engine.metrics
    registry = engine.registry

    engine.attach_subsystem("agents_engine",
                            AgentEngine(registry=registry, events=events,
                                        metrics=metrics))
    engine.attach_subsystem("planner_engine",
                            PlannerEngine(registry=registry, events=events,
                                          metrics=metrics))
    engine.attach_subsystem("executor_engine",
                            ExecutorEngine(events=events, metrics=metrics))
    engine.attach_subsystem("communication_engine",
                            CommunicationEngine(events=events,
                                                metrics=metrics))
    engine.attach_subsystem("memory_engine",
                            MemoryEngine(events=events, metrics=metrics))
    engine.attach_subsystem("decision_engine",
                            DecisionEngine(events=events, metrics=metrics))
    engine.attach_subsystem("evaluation_engine",
                            EvaluationEngine(metrics=metrics))
    engine.attach_subsystem("scheduling_engine",
                            SchedulingEngine(events=events, metrics=metrics))
    engine.attach_subsystem("learning_engine",
                            LearningEngine(metrics=metrics))
    return engine
