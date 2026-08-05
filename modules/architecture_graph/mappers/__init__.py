"""Mappers: turn platform entities (workflows, plugins, agents, security)
into graph nodes and relations.

Each mapper owns one entity family and knows how to discover it on disk and
wire it into the :class:`ArchitectureGraph`.
"""
from __future__ import annotations

from modules.architecture_graph.mappers.access_graph import (
    AccessGraph,
    build_access_graph,
)
from modules.architecture_graph.mappers.agent_mapper import (
    AgentMapper,
    discover_agents,
)
from modules.architecture_graph.mappers.agent_monitor import AgentMonitor
from modules.architecture_graph.mappers.agent_relations import AgentRelations
from modules.architecture_graph.mappers.permission_mapper import (
    PermissionMapper,
    discover_permissions,
)
from modules.architecture_graph.mappers.plugin_discovery import PluginDiscovery
from modules.architecture_graph.mappers.plugin_graph import build_plugin_graph
from modules.architecture_graph.mappers.plugin_registry import PluginRegistry
from modules.architecture_graph.mappers.trust_graph import TrustGraph
from modules.architecture_graph.mappers.workflow_execution_map import (
    WorkflowExecutionMap,
    build_execution_map,
)
from modules.architecture_graph.mappers.workflow_graph import (
    WorkflowGraph,
    build_workflow_graph,
)
from modules.architecture_graph.mappers.workflow_mapper import WorkflowMapper

__all__ = [
    "AccessGraph",
    "AgentMapper",
    "AgentMonitor",
    "AgentRelations",
    "PermissionMapper",
    "PluginDiscovery",
    "PluginRegistry",
    "TrustGraph",
    "WorkflowExecutionMap",
    "WorkflowGraph",
    "WorkflowMapper",
    "build_access_graph",
    "build_execution_map",
    "build_plugin_graph",
    "build_workflow_graph",
    "discover_agents",
    "discover_permissions",
]
