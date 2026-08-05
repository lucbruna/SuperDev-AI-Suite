"""Plugin graph: focused subgraph over plugins and their dependencies."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.edge_builder import depends_on
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import plugin_node
from modules.architecture_graph.mappers.plugin_registry import PluginRegistry


class PluginGraph:
    """Standalone plugin dependency graph."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.graph = ArchitectureGraph(name="plugins", project_root=root)

    def build(self) -> ArchitectureGraph:
        registry = PluginRegistry(self.root)
        plugins = registry.discover()
        for plugin in plugins:
            name = plugin.get("name", "")
            if not name:
                continue
            node_id = f"plugin:{name}"
            if not self.graph.has_node(node_id):
                node = plugin_node(name, plugin.get("path", ""))
                node.meta = {"version": plugin.get("version", "")}
                self.graph.add_node(node)
            for dep in plugin.get("dependencies", []):
                if not dep:
                    continue
                dep_id = f"plugin:{dep}"
                if not self.graph.has_node(dep_id):
                    self.graph.add_node(plugin_node(dep, f"plugins/{dep}/"))
                self.graph.add_edge(depends_on(node_id, dep_id))
        return self.graph

    def to_dict(self) -> dict[str, Any]:
        return self.graph.to_dict()


def build_plugin_graph(root: str) -> ArchitectureGraph:
    """One-shot convenience helper."""
    return PluginGraph(root).build()
