"""Workflow mapper: map workflow definitions onto the architecture graph.

Takes the records produced by :mod:`workflow_scanner` and turns them into
graph nodes and edges: workflow nodes, their declared agents, steps and the
plugins/services they depend on.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.edge_builder import depends_on, uses
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import workflow_node
from modules.architecture_graph.scanner import workflow_scanner


class WorkflowMapper:
    """Registers workflow nodes + relations on the graph."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.records: list[dict[str, Any]] = []

    def scan(self) -> list[dict[str, Any]]:
        self.records = workflow_scanner.scan(self.root)
        return self.records

    def apply(self, graph: ArchitectureGraph) -> int:
        """Add workflow nodes and edges. Returns number of workflows added."""
        if not self.records:
            self.scan()
        added = 0
        for record in self.records:
            name = record.get("name", "")
            if not name:
                continue
            node_id = f"workflow:{name}"
            if not graph.has_node(node_id):
                node = workflow_node(name, record.get("path", ""))
                node.meta = {
                    "format": record.get("format", ""),
                    "steps": record.get("steps", []),
                }
                graph.add_node(node)
                added += 1
            # Declared agents -> edges.
            for agent in record.get("agents", []):
                if agent and graph.has_node(f"agent:{agent}"):
                    graph.add_edge(uses(node_id, f"agent:{agent}"))
        return added

    def workflow_by_name(self, name: str) -> dict[str, Any] | None:
        if not self.records:
            self.scan()
        for record in self.records:
            if record.get("name") == name:
                return record
        return None

    def summary(self) -> dict[str, Any]:
        if not self.records:
            self.scan()
        formats: dict[str, int] = {}
        for record in self.records:
            fmt = record.get("format", "?")
            formats[fmt] = formats.get(fmt, 0) + 1
        return {"total": len(self.records), "by_format": formats}
