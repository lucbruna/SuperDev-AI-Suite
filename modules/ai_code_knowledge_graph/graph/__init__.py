"""Knowledge graph package — nodes, edges and the graph builder.

Kept dependency-free of ``core`` (no imports of the core package at module
level) so it can be imported safely from anywhere, including the runtime
wiring. Analyzer registration happens in ``core.knowledge_runtime``.
"""
from __future__ import annotations

from modules.ai_code_knowledge_graph.graph.builder import KnowledgeGraphBuilder
from modules.ai_code_knowledge_graph.graph.edges import CALLS, CONTAINS, DEPENDS_ON, IMPORTS, REFERENCES, make_edge
from modules.ai_code_knowledge_graph.graph.nodes import (
    file_node_id,
    make_file_node,
    make_node,
    node_id,
)

__all__ = [
    "CALLS",
    "CONTAINS",
    "DEPENDS_ON",
    "IMPORTS",
    "REFERENCES",
    "KnowledgeGraphBuilder",
    "file_node_id",
    "make_edge",
    "make_file_node",
    "make_node",
    "node_id",
]
