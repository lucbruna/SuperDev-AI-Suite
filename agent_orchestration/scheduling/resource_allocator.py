"""Resource allocation of tasks to agents (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_models import AgentProfile, AgentTask


class ResourceAllocator:
    """Assigns tasks to capable agents while tracking load."""

    def __init__(self) -> None:
        self._load: dict[str, int] = {}

    def assign(self, task: AgentTask,
               agents: list[AgentProfile]) -> AgentProfile | None:
        for agent in agents:
            if agent.status.value != "idle":
                continue
            if agent.capabilities and task.title:
                matched = any(capability.name.lower()
                              in task.title.lower()
                              for capability in agent.capabilities)
                if not matched:
                    continue
            if self._load.get(agent.agent_id, 0) >= max(
                    (capability.max_load for capability in agent.capabilities),
                    default=1):
                continue
            task.agent_id = agent.agent_id
            self._load[agent.agent_id] = self._load.get(agent.agent_id, 0) + 1
            return agent
        return None

    def release(self, agent_id: str) -> None:
        if agent_id in self._load:
            self._load[agent_id] = max(0, self._load[agent_id] - 1)
            if self._load[agent_id] == 0:
                del self._load[agent_id]

    def load(self, agent_id: str) -> int:
        return self._load.get(agent_id, 0)

    def summary(self) -> dict[str, Any]:
        return {"assigned": sum(self._load.values()),
                "by_agent": dict(self._load)}
