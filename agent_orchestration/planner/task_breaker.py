"""Task breaking for the planner (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_models import (AgentTask, Priority,
                                                     RiskLevel, TaskStatus)
from agent_orchestration.orchestrator_protocols import new_id

_STANDARD_PIPELINE = [
    "Analisar requisitos",
    "Criar arquitetura",
    "Criar banco de dados",
    "Desenvolver API",
    "Criar interface",
    "Testar",
    "Publicar",
]


class TaskBreaker:
    """Breaks a request into ordered AgentTask steps."""

    def _make(self, title: str, description: str,
              plan_id: str) -> AgentTask:
        return AgentTask(
            task_id=new_id("task"), title=title, description=description,
            plan_id=plan_id, priority=Priority.MEDIUM,
            status=TaskStatus.PENDING, risk_level=RiskLevel.LOW)

    def break_down(self, request: str, plan_id: str = "") -> list[AgentTask]:
        return self.custom(_STANDARD_PIPELINE, plan_id)

    def custom(self, steps: list[str], plan_id: str = "") -> list[AgentTask]:
        return [self._make(step, "", plan_id) for step in steps]

    def single(self, title: str, description: str = "",
               plan_id: str = "") -> AgentTask:
        return self._make(title, description, plan_id)
