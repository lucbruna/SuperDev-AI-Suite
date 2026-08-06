"""Connector to the Autonomous Developer module."""
from __future__ import annotations

from modules.ai_evolution_engine.integrations.integration_registry import (
    ModuleConnector,
)


class AutonomousDeveloperConnector(ModuleConnector):
    """Exposes the autonomous coding pipeline."""

    name = "autonomous_developer"
    description = "Self-directed coding agent that plans, generates and tests code."
    module = "modules.autonomous_developer"
    public_api = ()


AUTONOMOUS_DEVELOPER = AutonomousDeveloperConnector()
