"""Connector to the Self-Healing Engine module."""
from __future__ import annotations

from modules.ai_evolution_engine.integrations.integration_registry import (
    ModuleConnector,
)


class SelfHealingConnector(ModuleConnector):
    """Exposes the healing engine's public API."""

    name = "self_healing"
    description = "Detects, diagnoses and repairs platform health issues."
    module = "modules.self_healing_engine"
    public_api = (
        "HealingEngine",
        "HealingManager",
        "HealingKernel",
        "HealingState",
        "ManagerState",
    )


SELF_HEALING = SelfHealingConnector()
