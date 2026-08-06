"""The 12 Chief Agents and their registry."""
from __future__ import annotations

from modules.super_ai_orchestrator.agents.agents import CHIEF_AGENTS, ChiefAgent
from modules.super_ai_orchestrator.agents.registry import AgentRegistry

__all__ = ["ChiefAgent", "CHIEF_AGENTS", "AgentRegistry"]
