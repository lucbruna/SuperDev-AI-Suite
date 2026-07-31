"""Resource assignment for the planner (Volume 31)."""

from __future__ import annotations

from agent_orchestration.orchestrator_models import AgentTask

_DEFAULT_MAPPING = {
    "banco": "data",
    "api": "code",
    "interface": "code",
    "test": "test",
    "segur": "security",
    "public": "devops",
    "document": "documentation",
    "arquitetura": "coding",
}


class ResourcePlanner:
    """Assigns tasks to agents by capability."""

    def _capability_for(self, title: str,
                        capability_by_title: dict[str, str]) -> str:
        lowered = title.lower()
        mapping = capability_by_title or _DEFAULT_MAPPING
        for keyword, capability in mapping.items():
            if keyword in lowered:
                return capability
        return ""

    def assign(self, tasks: list[AgentTask], agents: list,
               capability_by_title: dict[str, str] | None = None) -> None:
        for task in tasks:
            capability = self._capability_for(task.title, capability_by_title or {})
            target = next((agent for agent in agents
                           if agent.has_capability(capability)), None)
            if target is None and agents:
                target = agents[0]
            if target is not None:
                task.agent_id = target.agent_id

    def plan_assignment(self, tasks: list[AgentTask], agents: list,
                        capability_by_title: dict[str, str] | None = None
                        ) -> dict[str, str]:
        self.assign(tasks, agents, capability_by_title)
        return {task.task_id: task.agent_id for task in tasks}
