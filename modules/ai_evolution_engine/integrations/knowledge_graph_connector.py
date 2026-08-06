"""Connector to the AI Code Knowledge Graph module."""
from __future__ import annotations

from modules.ai_evolution_engine.integrations.integration_registry import (
    ModuleConnector,
)


class KnowledgeGraphConnector(ModuleConnector):
    """Exposes the semantic knowledge base of the suite."""

    name = "knowledge_graph"
    description = "Semantic model of files, classes, APIs and their relations."
    module = "modules.ai_code_knowledge_graph"
    public_api = ()


KNOWLEDGE_GRAPH = KnowledgeGraphConnector()
