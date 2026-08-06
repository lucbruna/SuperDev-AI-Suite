"""AI Code Knowledge Graph — central knowledge base for the SuperDev AI Suite.

Unlike the Architecture Graph (which maps *structure*), this module builds a
*semantic model* of the codebase: files, classes, functions, APIs, databases,
agents, plugins, workflows, prompts, MCP tools, events and the relations
between them. The knowledge is stored as a graph, embedded for vector search
and exposed to agents, architecture modules and the dashboard.

Pipeline::

    project ─▶ filesystem scanner ─▶ language parsers ─▶ AST analysis
           ─▶ semantic engine ─▶ knowledge graph builder ─▶ embeddings
           ─▶ vector store ─▶ RAG engine ─▶ agents / dashboards
"""
from __future__ import annotations

from modules.ai_code_knowledge_graph.version import __version__

__all__ = ["__version__"]
