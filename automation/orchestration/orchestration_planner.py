"""Plans: decomposes goals into agent tasks."""

from __future__ import annotations

from automation.automation_protocols import new_id
from automation.orchestration.orchestration_models import (OrchestrationPlan,
                                                           OrchestrationTask)


class OrchestrationPlanner:
    """Creates execution plans from goals."""

    def plan(self, goal: str,
             agent_ids: list[str] | None = None) -> OrchestrationPlan:
        """Default software-development pipeline:
        planner -> developer -> tester + security -> devops."""
        agents = agent_ids or ["planner", "developer", "tester",
                               "security", "devops"]
        tasks = [
            OrchestrationTask("t1", "Planejar tarefas", agents[0], "plan"),
            OrchestrationTask("t2", "Desenvolver codigo", agents[1],
                              "implement", depends_on=["t1"]),
            OrchestrationTask("t3", "Validar com testes", agents[2],
                              "test", depends_on=["t2"]),
            OrchestrationTask("t4", "Revisar seguranca", agents[3],
                              "security_review", depends_on=["t2"]),
            OrchestrationTask("t5", "Publicar em producao", agents[4],
                              "deploy", depends_on=["t3", "t4"]),
        ]
        return OrchestrationPlan(new_id("plan"), goal, tasks)

    def custom(self, goal: str, tasks: list[OrchestrationTask],
               plan_id: str | None = None) -> OrchestrationPlan:
        return OrchestrationPlan(plan_id or new_id("plan"), goal, tasks)
