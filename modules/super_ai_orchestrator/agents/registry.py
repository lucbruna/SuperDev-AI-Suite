"""AgentRegistry — lookup and capability queries over the Chief Agents."""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.agents.agents import CHIEF_AGENTS, ChiefAgent


class AgentRegistry:
    """Registry of the 12 Chief Agents.

    Attributes:
        agents: name -> ChiefAgent.
    """

    def __init__(self, agents: tuple[ChiefAgent, ...] = CHIEF_AGENTS) -> None:
        self.agents: dict[str, ChiefAgent] = {a.name: a for a in agents}

    def get(self, name: str) -> ChiefAgent | None:
        return self.agents.get(name)

    def all(self) -> tuple[ChiefAgent, ...]:
        return tuple(self.agents.values())

    def names(self) -> tuple[str, ...]:
        return tuple(self.agents.keys())

    def capable_of(self, kind: str) -> tuple[str, ...]:
        """Agent names (in registration order) that can handle ``kind``."""
        return tuple(a.name for a in self.agents.values() if a.handles(kind))

    def tool_users(self, tool: str) -> tuple[str, ...]:
        return tuple(a.name for a in self.agents.values() if tool in a.tools)

    def to_dict(self) -> dict[str, Any]:
        return {"agents": [a.to_dict() for a in self.all()]}
