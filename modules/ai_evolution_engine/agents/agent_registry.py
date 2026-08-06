"""Agent registry: deterministic in-process agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.recommendation.recommendation_engine import (
    Recommendation,
)


@dataclass(slots=True)
class EvolutionAgent:
    """A named function-based agent participating in the pipeline."""

    name: str
    role: str
    enabled: bool = True
    handler: Callable[[EvolutionContext], list[Recommendation]] | None = None

    def run(self, ctx: EvolutionContext) -> list[Recommendation]:
        if not self.enabled or self.handler is None:
            return []
        return self.handler(ctx)


class AgentRegistry:
    """Registers and executes evolution agents."""

    def __init__(self) -> None:
        self._agents: dict[str, EvolutionAgent] = {}

    def register(self, agent: EvolutionAgent) -> None:
        self._agents[agent.name] = agent

    def unregister(self, name: str) -> None:
        self._agents.pop(name, None)

    def get(self, name: str) -> EvolutionAgent | None:
        return self._agents.get(name)

    def names(self) -> list[str]:
        return sorted(self._agents)

    def run_all(self, ctx: EvolutionContext) -> list[Recommendation]:
        results: list[Recommendation] = []
        for name in sorted(self._agents):
            agent = self._agents[name]
            if agent.enabled:
                results.extend(agent.run(ctx))
        return results
