"""AgentDispatcher: routes jobs to agents by capability and tracks availability."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

AGENT_STATUSES = ("available", "busy", "offline")


@dataclass
class Agent:
    name: str
    skills: list[str] = field(default_factory=list)
    status: str = "available"
    busy_jobs: list[str] = field(default_factory=list)


class AgentDispatcher:
    """In-memory agent registry and dispatch router."""

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, name: str, skills: list[str] | None = None) -> Agent:
        if name in self._agents:
            raise KeyError(f"agent {name!r} already registered")
        agent = Agent(name=name, skills=list(skills or []))
        self._agents[name] = agent
        return agent

    def unregister(self, name: str) -> bool:
        return self._agents.pop(name, None) is not None

    def get(self, name: str) -> Agent | None:
        return self._agents.get(name)

    def agents(self) -> list[str]:
        return sorted(self._agents)

    def skills_of(self, name: str) -> list[str]:
        agent = self.get(name)
        return list(agent.skills) if agent is not None else []

    def find_agent(self, skill: str) -> str | None:
        """First available registered agent that has the skill (deterministic)."""
        for name in sorted(self._agents):
            agent = self._agents[name]
            if agent.status == "available" and skill in agent.skills:
                return name
        return None

    def dispatch(self, name: str, job_id: str, skill: str | None = None) -> bool:
        agent = self.get(name)
        if agent is None or agent.status != "available":
            return False
        if skill is not None and skill not in agent.skills:
            return False
        agent.status = "busy"
        agent.busy_jobs.append(job_id)
        return True

    def release(self, name: str, job_id: str) -> bool:
        """Mark the agent free after a job completes or fails."""
        agent = self.get(name)
        if agent is None:
            return False
        if job_id in agent.busy_jobs:
            agent.busy_jobs.remove(job_id)
        if not agent.busy_jobs:
            agent.status = "available"
        return True

    def set_status(self, name: str, status: str) -> bool:
        if status not in AGENT_STATUSES:
            raise ValueError(f"invalid agent status {status!r}; expected one of {AGENT_STATUSES}")
        agent = self.get(name)
        if agent is None:
            return False
        agent.status = status
        if status != "busy":
            agent.busy_jobs = []
        return True

    def stats(self) -> dict[str, Any]:
        return {
            "total": len(self._agents),
            "available": sum(1 for a in self._agents.values() if a.status == "available"),
            "busy": sum(1 for a in self._agents.values() if a.status == "busy"),
            "offline": sum(1 for a in self._agents.values() if a.status == "offline"),
        }
