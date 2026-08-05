"""Plugin registry: index of platform plugins and their capabilities.

Registers plugin nodes on the graph (name, path, version, dependencies) and
provides lookup helpers used by the plugin graph, discovery and the unused
plugin detector.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import plugin_node
from modules.architecture_graph.scanner.plugin_scanner import scan as scan_plugins


class PluginRegistry:
    """Registry over discovered plugins."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.plugins: list[dict[str, Any]] = []

    def discover(self) -> list[dict[str, Any]]:
        self.plugins = scan_plugins(self.root)
        return self.plugins

    def apply(self, graph: ArchitectureGraph) -> int:
        """Add plugin nodes + dependency edges to the graph."""
        if not self.plugins:
            self.discover()
        added = 0
        for plugin in self.plugins:
            name = plugin.get("name", "")
            if not name:
                continue
            node_id = f"plugin:{name}"
            if not graph.has_node(node_id):
                node = plugin_node(name, plugin.get("path", ""))
                node.meta = {"version": plugin.get("version", "")}
                graph.add_node(node)
                added += 1
            for dep in plugin.get("dependencies", []):
                if dep and graph.has_node(f"plugin:{dep}"):
                    from modules.architecture_graph.graph.edge_builder import depends_on

                    graph.add_edge(depends_on(node_id, f"plugin:{dep}"))
        return added

    def get(self, name: str) -> dict[str, Any] | None:
        if not self.plugins:
            self.discover()
        for plugin in self.plugins:
            if plugin.get("name") == name:
                return plugin
        return None

    def names(self) -> list[str]:
        if not self.plugins:
            self.discover()
        return [p.get("name", "") for p in self.plugins if p.get("name")]

    def summary(self) -> dict[str, Any]:
        if not self.plugins:
            self.discover()
        return {
            "total": len(self.plugins),
            "with_dependencies": sum(
                1 for p in self.plugins if p.get("dependencies")
            ),
        }
