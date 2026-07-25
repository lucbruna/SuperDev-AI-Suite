from __future__ import annotations

import uuid
from collections import deque
from typing import Any

from pydantic import BaseModel, Field

from workflow_engine.graph.edge import WorkflowEdge
from workflow_engine.graph.node import WorkflowNode


class WorkflowGraph(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nodes: dict[str, WorkflowNode] = Field(default_factory=dict)
    edges: dict[str, WorkflowEdge] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def add_node(self, node: WorkflowNode) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: WorkflowEdge) -> None:
        self.edges[edge.id] = edge

    def remove_node(self, node_id: str) -> None:
        self.nodes.pop(node_id, None)
        self.edges = {eid: e for eid, e in self.edges.items() if e.source_node_id != node_id and e.target_node_id != node_id}

    def remove_edge(self, edge_id: str) -> None:
        self.edges.pop(edge_id, None)

    def get_node(self, node_id: str) -> WorkflowNode | None:
        return self.nodes.get(node_id)

    def get_edges(self, from_node: str | None = None) -> list[WorkflowEdge]:
        if from_node:
            return [e for e in self.edges.values() if e.source_node_id == from_node]
        return list(self.edges.values())

    def topological_sort(self) -> list[WorkflowNode]:
        in_degree: dict[str, int] = {nid: 0 for nid in self.nodes}
        for edge in self.edges.values():
            in_degree[edge.target_node_id] = in_degree.get(edge.target_node_id, 0) + 1
        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        result = []
        while queue:
            nid = queue.popleft()
            result.append(self.nodes[nid])
            for edge in self.get_edges(nid):
                in_degree[edge.target_node_id] -= 1
                if in_degree[edge.target_node_id] == 0:
                    queue.append(edge.target_node_id)
        return result

    def validate(self) -> list[str]:
        errors = []
        if not self.nodes:
            errors.append("Graph must have at least one node")
        for edge in self.edges.values():
            if edge.source_node_id not in self.nodes:
                errors.append(f"Edge {edge.id} references missing source node {edge.source_node_id}")
            if edge.target_node_id not in self.nodes:
                errors.append(f"Edge {edge.id} references missing target node {edge.target_node_id}")
        try:
            sorted_nodes = self.topological_sort()
            if len(sorted_nodes) != len(self.nodes):
                errors.append("Graph contains a cycle")
        except Exception as e:
            errors.append(f"Topological sort failed: {e}")
        return errors

    def get_children(self, node_id: str) -> list[WorkflowNode]:
        children = []
        for edge in self.edges.values():
            if edge.source_node_id == node_id:
                child = self.nodes.get(edge.target_node_id)
                if child:
                    children.append(child)
        return children
