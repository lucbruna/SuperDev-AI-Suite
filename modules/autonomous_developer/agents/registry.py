"""Agent registry: named agents with deterministic dispatch."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from modules.autonomous_developer.agents.base import AgentResult, BaseAgent, timed_run
from modules.autonomous_developer.core.exceptions import ExecutionError

if TYPE_CHECKING:
    from modules.autonomous_developer.core.context import DeveloperContext

__all__ = ["AgentRegistry"]


class AgentRegistry:
    """Holds named agents; ``run`` dispatches and never raises on agent code."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> BaseAgent:
        """Register an agent under ``agent.name`` (overwrites on conflict)."""
        self._agents[agent.name] = agent
        return agent

    def get(self, name: str) -> BaseAgent:
        """Fetch an agent by name; raises :class:`ExecutionError` if unknown."""
        try:
            return self._agents[name]
        except KeyError:
            raise ExecutionError(f"Unknown agent: {name!r}") from None

    def names(self) -> list[str]:
        """All registered agent names, in registration order."""
        return list(self._agents)

    def run(self, name: str, ctx: DeveloperContext, goal: str, **kwargs: Any) -> AgentResult:
        """Dispatch to a named agent, converting exceptions into error results."""
        return timed_run(self.get(name), ctx, goal, **kwargs)
