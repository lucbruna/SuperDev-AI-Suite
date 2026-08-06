"""Connector to the Architecture Graph module."""
from __future__ import annotations

from modules.ai_evolution_engine.integrations.integration_registry import (
    ModuleConnector,
)


class ArchitectureGraphConnector(ModuleConnector):
    """Exposes the architecture graph's engine and build helpers."""

    name = "architecture_graph"
    description = "Maps the repository structure, dependencies and topology."
    module = "modules.architecture_graph"
    public_api = ("build_graph", "load_graph", "ArchitectureGraph")


ARCHITECTURE_GRAPH = ArchitectureGraphConnector()
