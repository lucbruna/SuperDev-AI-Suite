"""Node graph — explicit graph data structure (validation + topological order)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node:
    id: str
    op: str
    params: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, str] = field(default_factory=dict)


class NodeGraph:
    """Stores nodes and connections; exposes a topological evaluation order."""

    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}

    def add(self, node: Node) -> NodeGraph:
        if node.id in self.nodes:
            raise ValueError(f"duplicate node id {node.id!r}")
        self.nodes[node.id] = node
        return self

    def connect(self, src: str, port: str, dst: str) -> NodeGraph:
        if src not in self.nodes or dst not in self.nodes:
            raise ValueError("connection references unknown node")
        self.nodes[dst].inputs[port] = src
        return self

    def topological_order(self) -> list[str]:
        """Return node ids in dependency order (Kahn's algorithm)."""
        indeg = {nid: 0 for nid in self.nodes}
        deps: dict[str, list[str]] = {nid: [] for nid in self.nodes}
        for nid, node in self.nodes.items():
            for src in node.inputs.values():
                deps[src].append(nid)
                indeg[nid] += 1
        queue = [nid for nid, d in indeg.items() if d == 0]
        order: list[str] = []
        while queue:
            nid = queue.pop(0)
            order.append(nid)
            for nxt in deps[nid]:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    queue.append(nxt)
        if len(order) != len(self.nodes):
            raise ValueError("graph contains a cycle")
        return order
