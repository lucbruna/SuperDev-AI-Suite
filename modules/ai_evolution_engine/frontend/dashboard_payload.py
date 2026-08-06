"""Dashboard payload builder: serializes engine state for the frontend."""
from __future__ import annotations

from typing import Any

from modules.ai_evolution_engine.core.evolution_manager import EvolutionManager
from modules.ai_evolution_engine.integrations import build_default_registry


class DashboardPayload:
    """Builds a JSON-serializable dashboard payload."""

    def __init__(self, manager: EvolutionManager) -> None:
        self._manager = manager

    def build(self) -> dict[str, Any]:
        integrations = build_default_registry()
        return {
            "engine": self._manager.state().to_dict(),
            "integrations": integrations.summary(),
        }
