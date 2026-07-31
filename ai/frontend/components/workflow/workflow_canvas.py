"""
Workflow Canvas Component
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    START = "start"
    END = "end"
    ACTION = "action"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    ERROR_HANDLER = "error_handler"


class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowNode:
    id: str
    node_type: NodeType
    label: str
    x: float = 0
    y: float = 0
    status: NodeStatus = NodeStatus.PENDING
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    source: str
    target: str
    label: str = ""
    condition: str = ""


class WorkflowCanvas:
    def __init__(self):
        self.nodes: list[WorkflowNode] = []
        self.edges: list[WorkflowEdge] = []
        self.selected_node_id: str | None = None
        self.zoom: float = 1.0
        self.pan_x: float = 0
        self.pan_y: float = 0

    def add_node(self, node: WorkflowNode) -> None:
        self.nodes.append(node)

    def remove_node(self, node_id: str) -> None:
        self.nodes = [n for n in self.nodes if n.id != node_id]
        self.edges = [e for e in self.edges if e.source != node_id and e.target != node_id]

    def add_edge(self, edge: WorkflowEdge) -> None:
        self.edges.append(edge)

    def select_node(self, node_id: str) -> None:
        self.selected_node_id = node_id

    def update_node_status(self, node_id: str, status: NodeStatus) -> None:
        for node in self.nodes:
            if node.id == node_id:
                node.status = status
                return

    def zoom_in(self) -> None:
        self.zoom = min(2.0, self.zoom + 0.1)

    def zoom_out(self) -> None:
        self.zoom = max(0.25, self.zoom - 0.1)

    def fit_to_view(self) -> None:
        self.zoom = 1.0
        self.pan_x = 0
        self.pan_y = 0

    def render(self) -> dict[str, Any]:
        return {
            "nodes": [{"id": n.id, "type": n.node_type.value, "label": n.label, "status": n.status.value} for n in self.nodes],
            "edges": [{"source": e.source, "target": e.target} for e in self.edges],
            "zoom": self.zoom,
            "selectedNode": self.selected_node_id,
        }
