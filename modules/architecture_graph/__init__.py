"""Architecture Graph — native module that discovers, maps and visualizes the
whole SuperDev AI Suite architecture.

The module builds a dependency graph of the repository (modules, files,
APIs, agents, plugins, workflows, databases), analyzes it (impact, cycles,
orphans, dead code, coupling, topology) and exposes it through a REST API,
WebSocket events, CLI tools and multiple export formats.
"""

from __future__ import annotations

__version__ = "1.0.0"
__all__ = [
    "__version__",
    "build_graph",
    "load_graph",
    "ArchitectureGraph",
    "GraphNode",
    "GraphEdge",
]

from modules.architecture_graph.core.architecture_engine import (
    ArchitectureEngine,
    build_graph,
    load_graph,
)
from modules.architecture_graph.graph.graph_builder import (
    ArchitectureGraph,
    GraphEdge,
    GraphNode,
)
