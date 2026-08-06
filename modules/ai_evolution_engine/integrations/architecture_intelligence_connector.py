"""Connector to the Architecture Intelligence module."""
from __future__ import annotations

from modules.ai_evolution_engine.integrations.integration_registry import (
    ModuleConnector,
)


class ArchitectureIntelligenceConnector(ModuleConnector):
    """Exposes strategic insights, forecasts and recommendations."""

    name = "architecture_intelligence"
    description = "Strategic/temporal layer on top of the architecture graph."
    module = "modules.architecture_intelligence"
    public_api = ("ArchitectureIntelligenceEngine", "get_intelligence")


ARCHITECTURE_INTELLIGENCE = ArchitectureIntelligenceConnector()
