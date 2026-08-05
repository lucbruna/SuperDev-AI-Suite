"""Workflow definitions: declarative graph of nodes and edges with conditions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional

#: node function: (context, node) -> result
NodeFunc = Callable[[dict[str, Any], "WorkflowNode"], Any]
#: edge condition: (context, source_result) -> bool
ConditionFunc = Callable[[dict[str, Any], Any], bool]


@dataclass
class WorkflowNode:
    node_id: str
    type: str = "task"
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"node_id": self.node_id, "type": self.type, "params": dict(self.params)}


@dataclass
class WorkflowEdge:
    source: str
    target: str
    condition: Optional[ConditionFunc] = None

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "target": self.target}


@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str = ""
    version: str = "1.0.0"
    nodes: list[WorkflowNode] = field(default_factory=list)
    edges: list[WorkflowEdge] = field(default_factory=list)

    def node(self, node_id: str) -> Optional[WorkflowNode]:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "version": self.version,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }
