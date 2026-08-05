"""Core graph data model: nodes, edges and the :class:`ArchitectureGraph`.

This module is the single source of truth for the graph structure used by
every other part of the Architecture Graph module and by Architecture
Intelligence (which consumes the same model through the storage layer).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Iterator

from modules.architecture_graph.config.graph_constants import (
    EDGE_KINDS,
    LAYER_ORDER,
    LAYERS,
    NODE_KINDS,
)


@dataclass(slots=True)
class GraphNode:
    """A node in the architecture graph.

    ``id`` is unique. ``kind`` must be one of :data:`NODE_KINDS`. ``layer``
    is derived from the path (see :func:`layer_of`). ``meta`` carries
    arbitrary per-kind attributes (e.g. ``{"method": "GET"}`` for APIs).
    """

    id: str
    name: str
    kind: str = "file"
    language: str = ""
    path: str = ""
    size: int = 0
    layer: str = ""
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in NODE_KINDS and self.kind != "root":
            self.kind = "file"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "language": self.language,
            "path": self.path,
            "size": self.size,
            "layer": self.layer,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphNode":
        return cls(
            id=str(data["id"]),
            name=str(data.get("name", "")),
            kind=str(data.get("kind", "file")),
            language=str(data.get("language", "")),
            path=str(data.get("path", "")),
            size=int(data.get("size", 0)),
            layer=str(data.get("layer", "")),
            meta=dict(data.get("meta") or {}),
        )


@dataclass(slots=True)
class GraphEdge:
    """A directed edge between two nodes."""

    source: str
    target: str
    kind: str = "depends_on"
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in EDGE_KINDS:
            self.kind = "depends_on"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "kind": self.kind,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GraphEdge":
        return cls(
            source=str(data["source"]),
            target=str(data["target"]),
            kind=str(data.get("kind", "depends_on")),
            meta=dict(data.get("meta") or {}),
        )


def layer_of(rel_path: str) -> str:
    """Derive the architecture layer from a repo-relative path."""
    if not rel_path:
        return ""
    parts = rel_path.replace("\\", "/").split("/")
    for i, part in enumerate(parts):
        if part in LAYERS:
            return LAYERS[part]
        if i == 0:
            # First segment may be a module/package name under a known layer.
            for layer_dir, layer in LAYERS.items():
                if part.startswith(layer_dir):
                    return layer
    return "external" if parts[0] in {"node_modules", "site-packages"} else ""


def layer_index(layer: str) -> int:
    """Position of a layer in the dependency ordering (lower = more basic)."""
    return LAYER_ORDER.index(layer) if layer in LAYER_ORDER else len(LAYER_ORDER)


class ArchitectureGraph:
    """In-memory directed graph of the platform architecture."""

    def __init__(self, name: str = "superdev", project_root: str = "") -> None:
        self.name = name
        self.project_root = project_root
        self.version = 1
        self.built_at = datetime.now(timezone.utc).isoformat()
        self._nodes: dict[str, GraphNode] = {}
        self._edges: list[GraphEdge] = []
        self._out: dict[str, set[str]] = {}
        self._in: dict[str, set[str]] = {}

    # ------------------------------------------------------------------ nodes
    def add_node(self, node: GraphNode) -> bool:
        """Add a node. Returns False when the id already exists."""
        if node.id in self._nodes:
            return False
        self._nodes[node.id] = node
        self._out.setdefault(node.id, set())
        self._in.setdefault(node.id, set())
        return True

    def upsert_node(self, node: GraphNode) -> None:
        if node.id in self._nodes:
            self._nodes[node.id] = node
            return
        self.add_node(node)

    def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    def has_node(self, node_id: str) -> bool:
        return node_id in self._nodes

    def remove_node(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        del self._nodes[node_id]
        self._out.pop(node_id, None)
        self._in.pop(node_id, None)
        self._edges = [
            e for e in self._edges if e.source != node_id and e.target != node_id
        ]
        for targets in self._out.values():
            targets.discard(node_id)
        for sources in self._in.values():
            sources.discard(node_id)
        return True

    def nodes(self) -> list[GraphNode]:
        return list(self._nodes.values())

    def node_ids(self) -> list[str]:
        return list(self._nodes.keys())

    def nodes_by_kind(self, kind: str) -> list[GraphNode]:
        return [n for n in self._nodes.values() if n.kind == kind]

    # ------------------------------------------------------------------ edges
    def add_edge(self, edge: GraphEdge) -> bool:
        """Add an edge. Returns False when an endpoint does not exist or the
        edge is a duplicate (same source/target/kind)."""
        if edge.source not in self._nodes or edge.target not in self._nodes:
            return False
        if edge.source == edge.target:
            return False
        if any(
            e.source == edge.source and e.target == edge.target and e.kind == edge.kind
            for e in self._edges
        ):
            return False
        self._edges.append(edge)
        self._out[edge.source].add(edge.target)
        self._in[edge.target].add(edge.source)
        return True

    def edges(self) -> list[GraphEdge]:
        return list(self._edges)

    def edges_of(self, kind: str) -> list[GraphEdge]:
        return [e for e in self._edges if e.kind == kind]

    # ------------------------------------------------------------------ query
    def outgoing(self, node_id: str) -> list[str]:
        """Direct dependencies of a node."""
        return sorted(self._out.get(node_id, set()))

    def incoming(self, node_id: str) -> list[str]:
        """Direct dependents of a node."""
        return sorted(self._in.get(node_id, set()))

    def neighbors(self, node_id: str) -> list[str]:
        return sorted(self._out.get(node_id, set()) | self._in.get(node_id, set()))

    def edges_between(self, source: str, target: str) -> list[GraphEdge]:
        return [
            e
            for e in self._edges
            if e.source == source and e.target == target
        ]

    def nodes_matching(self, query: str, *, kinds: Iterable[str] | None = None) -> list[GraphNode]:
        """Case-insensitive substring match over name/path/id."""
        q = query.lower()
        selected: set[str] = set(kinds) if kinds is not None else set()
        results: list[GraphNode] = []
        for node in self._nodes.values():
            if selected and node.kind not in selected:
                continue
            if q in node.id.lower() or q in node.name.lower() or q in node.path.lower():
                results.append(node)
        return results

    def subgraph(self, node_ids: Iterable[str]) -> "ArchitectureGraph":
        """Return a new graph containing only the given nodes and the edges
        between them."""
        ids = set(node_ids)
        sub = ArchitectureGraph(name=f"{self.name}:subgraph", project_root=self.project_root)
        for node_id in ids:
            node = self._nodes.get(node_id)
            if node is not None:
                sub._nodes[node_id] = node
        for edge in self._edges:
            if edge.source in ids and edge.target in ids:
                sub._edges.append(edge)
        for node_id in sub._nodes:
            sub._out[node_id] = {
                e.target for e in sub._edges if e.source == node_id
            }
            sub._in[node_id] = {
                e.source for e in sub._edges if e.target == node_id
            }
        return sub

    # ------------------------------------------------------------------ stats
    def stats(self) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for node in self._nodes.values():
            counts[node.kind] = counts.get(node.kind, 0) + 1
        layer_counts: dict[str, int] = {}
        for node in self._nodes.values():
            layer_counts[node.layer or "unknown"] = (
                layer_counts.get(node.layer or "unknown", 0) + 1
            )
        return {
            "name": self.name,
            "project_root": self.project_root,
            "built_at": self.built_at,
            "version": self.version,
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "kinds": counts,
            "layers": layer_counts,
        }

    # ------------------------------------------------------------------ serde
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "project_root": self.project_root,
            "version": self.version,
            "built_at": self.built_at,
            "nodes": [n.to_dict() for n in self._nodes.values()],
            "edges": [e.to_dict() for e in self._edges],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ArchitectureGraph":
        graph = cls(
            name=str(data.get("name", "superdev")),
            project_root=str(data.get("project_root", "")),
        )
        graph.version = int(data.get("version", 1))
        graph.built_at = str(data.get("built_at", ""))
        for raw in data.get("nodes", []):
            graph._nodes[str(raw["id"])] = GraphNode.from_dict(raw)
        for raw in data.get("edges", []):
            graph._edges.append(GraphEdge.from_dict(raw))
        for node_id in graph._nodes:
            graph._out[node_id] = {
                e.target for e in graph._edges if e.source == node_id
            }
            graph._in[node_id] = {
                e.source for e in graph._edges if e.target == node_id
            }
        return graph

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, payload: str) -> "ArchitectureGraph":
        return cls.from_dict(json.loads(payload))

    def __iter__(self) -> Iterator[GraphNode]:
        return iter(self._nodes.values())

    def __len__(self) -> int:
        return len(self._nodes)
