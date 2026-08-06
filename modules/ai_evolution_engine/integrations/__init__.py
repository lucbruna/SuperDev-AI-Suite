"""Integrations package for the AI Evolution Engine."""
from __future__ import annotations

from modules.ai_evolution_engine.integrations.architecture_graph_connector import (
    ARCHITECTURE_GRAPH,
)
from modules.ai_evolution_engine.integrations.architecture_intelligence_connector import (
    ARCHITECTURE_INTELLIGENCE,
)
from modules.ai_evolution_engine.integrations.autonomous_developer_connector import (
    AUTONOMOUS_DEVELOPER,
)
from modules.ai_evolution_engine.integrations.digital_twin_connector import (
    DIGITAL_TWIN,
)
from modules.ai_evolution_engine.integrations.integration_registry import (
    IntegrationConnector,
    IntegrationRegistry,
    ModuleConnector,
)
from modules.ai_evolution_engine.integrations.knowledge_graph_connector import (
    KNOWLEDGE_GRAPH,
)
from modules.ai_evolution_engine.integrations.self_healing_connector import (
    SELF_HEALING,
)
from modules.ai_evolution_engine.integrations.toolchain_connectors import (
    DockerConnector,
    GitHubConnector,
    GitConnector,
    KubernetesConnector,
    MCPConnector,
)

DEFAULT_CONNECTORS = (
    ARCHITECTURE_GRAPH,
    ARCHITECTURE_INTELLIGENCE,
    KNOWLEDGE_GRAPH,
    DIGITAL_TWIN,
    SELF_HEALING,
    AUTONOMOUS_DEVELOPER,
    GitConnector(),
    GitHubConnector(),
    DockerConnector(),
    KubernetesConnector(),
    MCPConnector(),
)


def build_default_registry() -> IntegrationRegistry:
    registry = IntegrationRegistry()
    for connector in DEFAULT_CONNECTORS:
        registry.register(connector)
    return registry


__all__ = [
    "IntegrationRegistry",
    "IntegrationConnector",
    "ModuleConnector",
    "build_default_registry",
    "DEFAULT_CONNECTORS",
]
