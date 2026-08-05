"""Navigation engine: graph queries for humans and AI.

Provides the primitive operations used by the API search endpoints and by the
Architecture Intelligence reasoning layer: find, where-used, reachability and
shortest-path between nodes.
"""
from __future__ import annotations

from collections import deque
from typing import Any, Iterable

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def find(
    graph: ArchitectureGraph,
    query: str,
    *,
    kinds: Iterable[str] | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    nodes = graph.nodes_matching(query, kinds=kinds)[:limit]
    return [_node_brief(graph, n.id) for n in nodes]


def _node_brief(graph: ArchitectureGraph, node_id: str) -> dict[str, Any]:
    node = graph.get_node(node_id)
    if node is None:
        return {"id": node_id}
    return {
        "id": node.id,
        "name": node.name,
        "kind": node.kind,
        "language": node.language,
        "path": node.path,
        "layer": node.layer,
        "size": node.size,
        "fan_in": len(graph.incoming(node_id)),
        "fan_out": len(graph.outgoing(node_id)),
    }


def where_used(graph: ArchitectureGraph, path: str) -> dict[str, Any]:
    """Find the file node for a path and all its dependents."""
    path = path.replace("\\", "/")
    node_id = f"file:{path}"
    if not graph.has_node(node_id):
        # Try prefix match.
        matches = [n.id for n in graph.nodes_matching(path, kinds={"file"})]
        if len(matches) == 1:
            node_id = matches[0]
        elif not matches:
            return {"node_id": None, "found": False, "dependents": []}
        else:
            return {"node_id": None, "found": False, "matches": matches, "dependents": []}
    dependents = [_node_brief(graph, nid) for nid in graph.incoming(node_id)]
    return {"node_id": node_id, "found": True, "dependents": dependents}


def path_between(graph: ArchitectureGraph, a: str, b: str) -> list[str]:
    """Shortest directed path from a to b (BFS). Empty when none exists."""
    if not graph.has_node(a) or not graph.has_node(b):
        return []
    if a == b:
        return [a]
    parent: dict[str, str | None] = {a: None}
    queue: deque[str] = deque([a])
    while queue:
        current = queue.popleft()
        for neighbor in graph.outgoing(current):
            if neighbor in parent:
                continue
            parent[neighbor] = current
            if neighbor == b:
                path = [b]
                node: str | None = b
                while node is not None:
                    prev = parent[node]
                    if prev is None:
                        break
                    path.append(prev)
                    node = prev
                return list(reversed(path))
            queue.append(neighbor)
    return []


def neighbors(
    graph: ArchitectureGraph, node_id: str, *, direction: str = "both"
) -> dict[str, Any]:
    if not graph.has_node(node_id):
        return {"node_id": node_id, "found": False}
    result: dict[str, Any] = {
        "node_id": node_id,
        "found": True,
        "incoming": [_node_brief(graph, nid) for nid in graph.incoming(node_id)],
        "outgoing": [_node_brief(graph, nid) for nid in graph.outgoing(node_id)],
    }
    return result


def reachable(
    graph: ArchitectureGraph, node_id: str, *, direction: str = "outgoing", max_depth: int = 12
) -> list[str]:
    if not graph.has_node(node_id):
        return []
    depth: dict[str, int] = {node_id: 0}
    queue: deque[str] = deque([node_id])
    while queue:
        current = queue.popleft()
        edges = graph.outgoing(current) if direction == "outgoing" else graph.incoming(current)
        for neighbor in edges:
            if neighbor in depth:
                continue
            d = depth[current] + 1
            if d > max_depth:
                continue
            depth[neighbor] = d
            queue.append(neighbor)
    return [nid for nid in depth if nid != node_id]
