"""Manager for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

import time
from typing import Any

from agent_orchestration.orchestrator_config import OrchestratorConfig
from agent_orchestration.orchestrator_context import OrchestratorContext
from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import (AgentMessage, AgentProfile,
                                                     AgentTask, MessageType,
                                                     Priority, RiskLevel,
                                                     TaskStatus)
from agent_orchestration.orchestrator_protocols import new_id
from agent_orchestration.orchestrator_registry import OrchestratorRegistry
from agent_orchestration.orchestrator_security import OrchestratorSecurity


class OrchestratorManager:
    """Core operations: agents, tasks, messages and approval flow."""

    def __init__(self, registry: OrchestratorRegistry,
                 events: OrchestratorEvents,
                 metrics: OrchestratorMetrics,
                 config: OrchestratorConfig,
                 context: OrchestratorContext,
                 security: OrchestratorSecurity,
                 engine: Any = None) -> None:
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.security = security
        self.engine = engine

    # -- agents --------------------------------------------------------------
    def register_agent(self, name: str, objective: str = "",
                       role: str = "worker",
                       capabilities: list[Any] | None = None,
                       tools: list[str] | None = None,
                       permissions: list[str] | None = None,
                       knowledge: list[str] | None = None,
                       limitations: list[str] | None = None) -> AgentProfile:
        agent = AgentProfile(
            agent_id=new_id("agent"), name=name, objective=objective,
            role=role, capabilities=list(capabilities or []),
            tools=list(tools or []), permissions=list(permissions or []),
            knowledge=list(knowledge or []), limitations=list(limitations or []),
            created_at=time.time())
        self.registry.register_agent(agent)
        self.metrics.increment("ao.agents")
        self.events.publish(OrchestratorEventType.AGENT_REGISTERED,
                            {"agent_id": agent.agent_id, "name": name})
        return agent

    def get_agent(self, agent_id: str) -> AgentProfile | None:
        return self.registry.get_agent(agent_id)

    def list_agents(self) -> list[AgentProfile]:
        return self.registry.list_agents()

    def remove_agent(self, agent_id: str) -> bool:
        if not self.registry.remove_agent(agent_id):
            return False
        self.metrics.increment("ao.agents", -1)
        self.events.publish(OrchestratorEventType.AGENT_REMOVED,
                            {"agent_id": agent_id})
        return True

    def set_agent_status(self, agent_id: str, status) -> bool:
        agent = self.registry.get_agent(agent_id)
        if agent is None:
            return False
        agent.status = status
        self.events.publish(OrchestratorEventType.AGENT_STATUS_CHANGED,
                            {"agent_id": agent_id,
                             "status": status.value})
        return True

    # -- tasks ---------------------------------------------------------------
    def create_task(self, title: str, description: str = "",
                    agent_id: str = "",
                    priority: Priority = Priority.MEDIUM,
                    risk_level: RiskLevel = RiskLevel.LOW,
                    approval_required: bool = False,
                    dependencies: list[str] | None = None,
                    plan_id: str = "") -> AgentTask:
        task = AgentTask(
            task_id=new_id("task"), title=title, description=description,
            agent_id=agent_id, plan_id=plan_id, priority=priority,
            risk_level=risk_level, approval_required=approval_required,
            dependencies=list(dependencies or []), created_at=time.time())
        self.registry.register_task(task)
        self.events.publish(OrchestratorEventType.TASK_PLANNED,
                            {"task_id": task.task_id, "title": title})
        return task

    def get_task(self, task_id: str) -> AgentTask | None:
        return self.registry.get_task(task_id)

    def list_tasks(self) -> list[AgentTask]:
        return self.registry.list_tasks()

    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        task = self.registry.get_task(task_id)
        if task is None:
            return False
        task.status = status
        now = time.time()
        if status == TaskStatus.RUNNING:
            task.started_at = now
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED,
                        TaskStatus.CANCELLED):
            task.completed_at = now
        event_map = {
            TaskStatus.QUEUED: OrchestratorEventType.TASK_QUEUED,
            TaskStatus.RUNNING: OrchestratorEventType.TASK_STARTED,
            TaskStatus.COMPLETED: OrchestratorEventType.TASK_COMPLETED,
            TaskStatus.FAILED: OrchestratorEventType.TASK_FAILED,
            TaskStatus.CANCELLED: OrchestratorEventType.TASK_CANCELLED,
        }
        if status in event_map:
            self.events.publish(event_map[status],
                                {"task_id": task_id, "status": status.value})
        return True

    def assign_task(self, task_id: str, agent_id: str) -> bool:
        task = self.registry.get_task(task_id)
        if task is None or self.registry.get_agent(agent_id) is None:
            return False
        task.agent_id = agent_id
        return True

    # -- messages ------------------------------------------------------------
    def send_message(self, sender_id: str, recipient_id: str,
                     content: str = "",
                     message_type: MessageType = MessageType.DIRECT,
                     payload: dict[str, Any] | None = None) -> AgentMessage:
        message = AgentMessage(
            message_id=new_id("message"), sender_id=sender_id,
            recipient_id=recipient_id, message_type=message_type,
            content=content, payload=dict(payload or {}),
            created_at=time.time())
        self.registry.record_message(message)
        self.metrics.increment("ao.messages")
        self.events.publish(OrchestratorEventType.MESSAGE_SENT,
                            {"message_id": message.message_id,
                             "sender_id": sender_id,
                             "recipient_id": recipient_id})
        return message

    def list_messages(self) -> list[AgentMessage]:
        return self.registry.list_messages()

    # -- approval flow -------------------------------------------------------
    def require_approval(self, task_id: str, reason: str = "") -> bool:
        task = self.registry.get_task(task_id)
        if task is None:
            return False
        task.status = TaskStatus.APPROVAL_REQUIRED
        self.events.publish(OrchestratorEventType.APPROVAL_REQUIRED,
                            {"task_id": task_id, "reason": reason})
        return True

    def resolve_approval(self, task_id: str, actor: str,
                         approved: bool) -> bool:
        task = self.registry.get_task(task_id)
        if task is None:
            return False
        if approved and not self.security.approve(actor):
            return False
        task.status = TaskStatus.QUEUED if approved else TaskStatus.CANCELLED
        self.events.publish(OrchestratorEventType.APPROVAL_RESOLVED,
                            {"task_id": task_id, "actor": actor,
                             "approved": approved})
        return True

    # -- stats ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "registry": self.registry.stats(),
            "metrics": self.metrics.snapshot(),
            "config": self.config.snapshot(),
            "context": self.context.snapshot(),
        }
