"""Connector to the Digital Twin module."""
from __future__ import annotations

from modules.ai_evolution_engine.integrations.integration_registry import (
    ModuleConnector,
)


class DigitalTwinConnector(ModuleConnector):
    """Exposes the living representation of the platform."""

    name = "digital_twin"
    description = "Living, continuously-synchronized representation of the platform."
    module = "modules.digital_twin"
    public_api = ("VERSION",)


DIGITAL_TWIN = DigitalTwinConnector()
