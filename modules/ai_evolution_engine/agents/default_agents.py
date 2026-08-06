"""Default evolution agents wired to the built-in analyzers."""
from __future__ import annotations

from modules.ai_evolution_engine.agents.agent_registry import AgentRegistry, EvolutionAgent
from modules.ai_evolution_engine.analytics.analytics_engine import AnalyticsEngine


def build_default_agents() -> AgentRegistry:
    registry = AgentRegistry()
    analytics = AnalyticsEngine()

    def analyst(ctx: object) -> list:
        analytics.compute(ctx)  # type: ignore[arg-type]
        return []

    registry.register(
        EvolutionAgent(
            name="analyst",
            role="compute analytics from context artifacts",
            handler=analyst,
        )
    )
    return registry
