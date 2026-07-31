from __future__ import annotations

from typing import Any


class KnowledgeGraph:
    """Graph structure for representing knowledge as nodes and edges."""

    def __init__(self):
        self._nodes: dict[str, dict[str, Any]] = {}
        self._edges: list[dict[str, Any]] = []

    @property
    def nodes(self) -> dict[str, dict[str, Any]]:
        return {k: dict(v) for k, v in self._nodes.items()}

    @property
    def edges(self) -> list[dict[str, Any]]:
        return [dict(e) for e in self._edges]

    def add_node(self, node_id: str, attributes: dict[str, Any] | None = None) -> None:
        if node_id not in self._nodes:
            self._nodes[node_id] = attributes or {}

    def remove_node(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        del self._nodes[node_id]
        self._edges = [e for e in self._edges if e["source"] != node_id and e["target"] != node_id]
        return True

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        node = self._nodes.get(node_id)
        return dict(node) if node else None

    def update_node(self, node_id: str, attributes: dict[str, Any]) -> bool:
        if node_id not in self._nodes:
            return False
        self._nodes[node_id].update(attributes)
        return True

    def add_edge(
        self,
        source: str,
        target: str,
        label: str = "",
        properties: dict[str, Any] | None = None,
    ) -> None:
        self._edges.append(
            {
                "source": source,
                "target": target,
                "label": label,
                "properties": properties or {},
            }
        )

    def remove_edges(self, source: str, target: str, label: str = "") -> int:
        before = len(self._edges)
        self._edges = [
            e
            for e in self._edges
            if not (e["source"] == source and e["target"] == target and (not label or e["label"] == label))
        ]
        return before - len(self._edges)

    def get_neighbors(self, node_id: str) -> list[dict[str, Any]]:
        neighbors: list[dict[str, Any]] = []
        for e in self._edges:
            if e["source"] == node_id:
                neighbor = self._nodes.get(e["target"])
                if neighbor:
                    neighbors.append({"node_id": e["target"], "attributes": dict(neighbor), "edge": dict(e)})
            elif e["target"] == node_id:
                neighbor = self._nodes.get(e["source"])
                if neighbor:
                    neighbors.append({"node_id": e["source"], "attributes": dict(neighbor), "edge": dict(e)})
        return neighbors

    def shortest_path(self, source: str, target: str) -> list[str] | None:
        if source not in self._nodes or target not in self._nodes:
            return None
        visited: set[str] = set()
        queue: list[tuple[str, list[str]]] = [(source, [source])]
        while queue:
            current, path = queue.pop(0)
            if current == target:
                return path
            if current in visited:
                continue
            visited.add(current)
            for e in self._edges:
                if e["source"] == current and e["target"] not in visited:
                    queue.append((e["target"], path + [e["target"]]))
                elif e["target"] == current and e["source"] not in visited:
                    queue.append((e["source"], path + [e["source"]]))
        return None

    def size(self) -> tuple[int, int]:
        return len(self._nodes), len(self._edges)

    def clear(self) -> None:
        self._nodes.clear()
        self._edges.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": {k: dict(v) for k, v in self._nodes.items()},
            "edges": [dict(e) for e in self._edges],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnowledgeGraph:
        graph = cls()
        for nid, attrs in data.get("nodes", {}).items():
            graph.add_node(nid, dict(attrs))
        for e in data.get("edges", []):
            graph.add_edge(e["source"], e["target"], e.get("label", ""), e.get("properties"))
        return graph
