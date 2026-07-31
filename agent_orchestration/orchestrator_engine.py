"""Agent Orchestration Engine facade (Volume 31).

Aggregate facade over the orchestration subsystems, exposing subsystem
engines lazily via ``engine.planner_engine`` once attached.
"""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_config import OrchestratorConfig
from agent_orchestration.orchestrator_context import OrchestratorContext
from agent_orchestration.orchestrator_events import OrchestratorEvents
from agent_orchestration.orchestrator_logger import get_logger
from agent_orchestration.orchestrator_manager import OrchestratorManager
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import (AgentMessage, AgentProfile,
                                                     AgentTask, MessageType,
                                                     Priority, RiskLevel,
                                                     TaskStatus)
from agent_orchestration.orchestrator_registry import OrchestratorRegistry
from agent_orchestration.orchestrator_runtime import OrchestratorRuntime
from agent_orchestration.orchestrator_security import OrchestratorSecurity


class OrchestratorEngine:
    """Aggregate facade over the orchestration subsystems."""

    def __init__(self, config: OrchestratorConfig | None = None,
                 events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None,
                 registry: OrchestratorRegistry | None = None,
                 security: OrchestratorSecurity | None = None,
                 context: OrchestratorContext | None = None,
                 runtime: OrchestratorRuntime | None = None) -> None:
        self._log = get_logger()
        self.config = config or OrchestratorConfig()
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()
        self.registry = registry or OrchestratorRegistry()
        self.security = security or OrchestratorSecurity()
        self.context = context or OrchestratorContext()
        self.runtime = runtime or OrchestratorRuntime()
        self.manager = OrchestratorManager(
            registry=self.registry, events=self.events, metrics=self.metrics,
            config=self.config, context=self.context, security=self.security,
            engine=self)
        self._subsystems: dict[str, Any] = {}

    # -- lifecycle ----------------------------------------------------------
    def start(self) -> bool:
        return self.runtime.start()

    def stop(self) -> bool:
        return self.runtime.stop()

    def run(self) -> bool:
        return self.start()

    # -- subsystem attachment ----------------------------------------------
    def attach_subsystem(self, name: str, engine: Any) -> None:
        self._subsystems[name] = engine
        setattr(self, name, engine)
        setattr(self.manager, name, engine)

    def __getattr__(self, name: str) -> Any:
        if name in self._subsystems:
            return self._subsystems[name]
        raise AttributeError(f"no subsystem or attribute '{name}'")

    # -- agent facade -------------------------------------------------------
    def register_agent(self, name: str, objective: str = "",
                       role: str = "worker",
                       capabilities: list[Any] | None = None,
                       tools: list[str] | None = None,
                       permissions: list[str] | None = None,
                       knowledge: list[str] | None = None,
                       limitations: list[str] | None = None) -> AgentProfile:
        return self.manager.register_agent(
            name, objective, role, capabilities, tools, permissions,
            knowledge, limitations)

    def get_agent(self, agent_id: str) -> AgentProfile | None:
        return self.manager.get_agent(agent_id)

    def list_agents(self) -> list[AgentProfile]:
        return self.manager.list_agents()

    def remove_agent(self, agent_id: str) -> bool:
        return self.manager.remove_agent(agent_id)

    # -- task facade --------------------------------------------------------
    def create_task(self, title: str, description: str = "",
                    agent_id: str = "",
                    priority: Priority = Priority.MEDIUM,
                    risk_level: RiskLevel = RiskLevel.LOW,
                    approval_required: bool = False,
                    dependencies: list[str] | None = None,
                    plan_id: str = "") -> AgentTask:
        return self.manager.create_task(
            title, description, agent_id, priority, risk_level,
            approval_required, dependencies, plan_id)

    def get_task(self, task_id: str) -> AgentTask | None:
        return self.manager.get_task(task_id)

    def list_tasks(self) -> list[AgentTask]:
        return self.manager.list_tasks()

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        return self.manager.update_task_status(task_id, status)

    def send_message(self, sender_id: str, recipient_id: str,
                     content: str = "",
                     message_type: MessageType = MessageType.DIRECT,
                     payload: dict[str, Any] | None = None) -> AgentMessage:
        return self.manager.send_message(
            sender_id, recipient_id, content, message_type, payload)

    def list_messages(self) -> list[AgentMessage]:
        return self.manager.list_messages()

    def require_approval(self, task_id: str, reason: str = "") -> bool:
        return self.manager.require_approval(task_id, reason)

    def resolve_approval(self, task_id: str, actor: str,
                         approved: bool) -> bool:
        return self.manager.resolve_approval(task_id, actor, approved)

    def set_agent_status(self, agent_id: str, status) -> bool:
        return self.manager.set_agent_status(agent_id, status)

    # -- misc ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "manager": self.manager.stats(),
            "subsystems": list(self._subsystems),
            "runtime": self.runtime.state(),
        }
