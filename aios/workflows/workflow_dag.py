"""WorkflowDAG: validates the workflow graph and computes deterministic orders."""
from __future__ import annotations

from typing import Any

from aios.workflows.workflow_definitions import WorkflowDefinition, WorkflowEdge


class WorkflowDAG:
    """Adjacency model over a :class:`WorkflowDefinition` with validation."""

    def __init__(self, definition: WorkflowDefinition) -> None:
        self.definition = definition
        self.nodes = {node.node_id: node for node in definition.nodes}
        self.incoming: dict[str, list[WorkflowEdge]] = {node_id: [] for node_id in self.nodes}
        self.outgoing: dict[str, list[WorkflowEdge]] = {node_id: [] for node_id in self.nodes}
        for edge in definition.edges:
            if edge.source in self.outgoing:
                self.outgoing[edge.source].append(edge)
            if edge.target in self.incoming:
                self.incoming[edge.target].append(edge)

    def validate(self) -> list[str]:
        """Return a sorted list of structural problems (empty when valid)."""
        problems: set[str] = set()
        seen: set[str] = set()
        for node in self.definition.nodes:
            if node.node_id in seen:
                problems.add(f"duplicate node id {node.node_id!r}")
            seen.add(node.node_id)
        for edge in self.definition.edges:
            if edge.source not in self.nodes:
                problems.add(f"unknown source {edge.source!r}")
            if edge.target not in self.nodes:
                problems.add(f"unknown target {edge.target!r}")
        if not self.definition.nodes:
            problems.add("workflow has no nodes")
        return sorted(problems)

    def is_acyclic(self) -> bool:
        try:
            self.topological_order()
            return True
        except ValueError:
            return False

    def topological_order(self) -> list[str]:
        """Kahn's algorithm; deterministic (sorted queues). Raises on cycles."""
        indegree = {node_id: len(self.incoming[node_id]) for node_id in self.nodes}
        queue = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
        order: list[str] = []
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            for edge in sorted(self.outgoing[node_id], key=lambda e: e.target):
                indegree[edge.target] -= 1
                if indegree[edge.target] == 0:
                    queue.append(edge.target)
                    queue.sort()
        if len(order) != len(self.nodes):
            raise ValueError(f"cycle detected in workflow {self.definition.workflow_id!r}")
        return order

    def node_ids(self) -> list[str]:
        return sorted(self.nodes)

    def edges_to(self, node_id: str) -> list[WorkflowEdge]:
        return list(self.incoming.get(node_id, []))

    def snapshot(self) -> dict[str, Any]:
        return {
            "workflow_id": self.definition.workflow_id,
            "node_count": len(self.nodes),
            "edge_count": sum(len(edges) for edges in self.outgoing.values()),
            "acyclic": self.is_acyclic(),
            "problems": self.validate(),
        }
