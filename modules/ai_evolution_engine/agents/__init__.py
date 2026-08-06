"""Agents package for the AI Evolution Engine."""
from __future__ import annotations

from modules.ai_evolution_engine.agents.agent_registry import (
    AgentRegistry,
    EvolutionAgent,
)
from modules.ai_evolution_engine.agents.default_agents import build_default_agents

__all__ = ["AgentRegistry", "EvolutionAgent", "build_default_agents"]
