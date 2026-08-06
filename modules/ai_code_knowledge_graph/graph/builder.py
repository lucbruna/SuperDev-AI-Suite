"""Knowledge graph builder — scan_result → {nodes, edges, stats}.

Consumes the normalized scanner output (files with ``parsed`` entity lists)
and produces a node/edge graph: file nodes, entity nodes contained in their
file, class → method containment, and import edges resolved against scanned
files. Registered as an ``analyzer`` so the pipeline index stage runs it and
stores the result in ``ctx.memory["knowledge_graph"]``.
"""
from __future__ import annotations

import logging
import posixpath
from typing import Any

from modules.ai_code_knowledge_graph.graph.edges import make_edge
from modules.ai_code_knowledge_graph.graph.nodes import make_file_node, make_node

logger = logging.getLogger(__name__)

_ENTITY_KEYS = frozenset({"kind", "name", "start_line", "end_line"})
_IMPORT_SUFFIXES = (
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".toml",
    ".ini",
    ".sh",
    ".sql",
)
_INDEX_FILES = ("__init__.py", "index.js", "index.ts", "index.jsx", "index.tsx")


class KnowledgeGraphBuilder:
    """Builds a normalized knowledge graph from a scan result."""

    def __init__(self, *, resolve_imports: bool = True) -> None:
        self.resolve_imports = resolve_imports

    # ── Analyzer interface (invoked by the pipeline index stage) ──────────
    def index(self, ctx) -> dict[str, Any]:
        """Analyzer hook: build the graph and store it on the context."""
        result = ctx.memory.get("scan_result")
        if not result:
            return {"nodes": 0, "edges": 0, "detail": "no scan result"}
        graph = self.build(result)
        ctx.memory.put("knowledge_graph", graph)
        ctx.record("graph_nodes", graph["stats"]["node_count"])
        ctx.record("graph_edges", graph["stats"]["edge_count"])
        return {
            "nodes": graph["stats"]["node_count"],
            "edges": graph["stats"]["edge_count"],
        }

    # ── Build ─────────────────────────────────────────────────────────────
    def build(self, scan_result: dict[str, Any]) -> dict[str, Any]:
        """Convert a scan result into a node/edge graph."""
        files = scan_result.get("files", [])
        by_path = {entry.get("rel_path"): entry for entry in files if entry.get("rel_path")}
        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, Any]] = []
        edge_keys: set[tuple[str, str, str]] = set()

        for entry in files:
            rel_path = entry.get("rel_path")
            if not rel_path:
                continue
            file_node = make_file_node(
                rel_path,
                language=entry.get("language"),
                size=entry.get("size"),
            )
            nodes[file_node["id"]] = file_node
            parsed = entry.get("parsed")
            if not isinstance(parsed, dict):
                continue
            for entity in parsed.get("entities", []):
                self._add_entity(nodes, edges, edge_keys, file_node, entity, by_path)

        return {
            "project_root": scan_result.get("project_root", ""),
            "nodes": sorted(nodes.values(), key=lambda node: node["id"]),
            "edges": edges,
            "stats": self._stats(nodes, edges),
        }

    # ── Helpers ────────────────────────────────────────────────────────────
    def _add_entity(
        self,
        nodes: dict[str, dict[str, Any]],
        edges: list[dict[str, Any]],
        edge_keys: set[tuple[str, str, str]],
        file_node: dict[str, Any],
        entity: dict[str, Any],
        by_path: dict[str, Any],
    ) -> None:
        kind = entity.get("kind", "unknown")
        if kind == "file":
            return  # the file node is created from the entry itself
        name = entity.get("name", "")
        line = entity.get("start_line", 1)
        end = entity.get("end_line", line)
        node = make_node(kind, name, file_node["name"], line, end, **self._extra(entity))
        if node["id"] in nodes:
            return
        nodes[node["id"]] = node
        self._add_edge(edges, edge_keys, file_node["id"], node["id"], "contains", line)

        if kind == "class":
            for method in entity.get("methods") or []:
                mname = method.get("name", "")
                mline = method.get("start_line", line)
                mend = method.get("end_line", mline)
                mnode = make_node("method", mname, file_node["name"], mline, mend, **self._extra(method))
                if mnode["id"] in nodes:
                    continue
                nodes[mnode["id"]] = mnode
                self._add_edge(edges, edge_keys, node["id"], mnode["id"], "contains", mline)

        if kind == "import":
            target = self._resolve_import(entity.get("source"), by_path, from_file=file_node["name"])
            if target:
                self._add_edge(edges, edge_keys, file_node["id"], target, "imports", line)

    @staticmethod
    def _extra(entity: dict[str, Any]) -> dict[str, Any]:
        return {key: value for key, value in entity.items() if key not in _ENTITY_KEYS}

    @staticmethod
    def _add_edge(
        edges: list[dict[str, Any]],
        edge_keys: set[tuple[str, str, str]],
        source: str,
        target: str,
        relation: str,
        line: int | None = None,
    ) -> None:
        key = (source, target, relation)
        if key in edge_keys:
            return
        edge_keys.add(key)
        edges.append(make_edge(source, target, relation, line=line))

    def _resolve_import(self, source: Any, by_path: dict[str, Any], from_file: str = "") -> str | None:
        """Resolve an import source to a scanned file node id, if possible.

        Relative sources (``./x``, ``../x``) are resolved against the
        importing file's directory; other sources are tried as project-root
        paths and, as a fallback, against the importing file's directory.
        """
        if not self.resolve_imports or not source:
            return None
        source_str = str(source).strip()
        if not source_str or source_str.startswith(("http://", "https://")):
            return None

        candidates: list[str] = []
        base_dir = posixpath.dirname(from_file)
        if source_str.startswith((".", "/")):
            joined = posixpath.normpath(posixpath.join(base_dir, source_str))
            candidates.append(joined.lstrip("/"))
        else:
            candidates.append(source_str)
            if base_dir:
                candidates.append(posixpath.normpath(posixpath.join(base_dir, source_str)))

        for candidate in candidates:
            if candidate in by_path:
                return make_file_node(candidate)["id"]
            for suffix in _IMPORT_SUFFIXES:
                if candidate + suffix in by_path:
                    return make_file_node(candidate + suffix)["id"]
            base = candidate.rstrip("/")
            for index in _INDEX_FILES:
                if f"{base}/{index}" in by_path:
                    return make_file_node(f"{base}/{index}")["id"]
        return None

    @staticmethod
    def _stats(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, Any]:
        nodes_by_kind: dict[str, int] = {}
        for node in nodes.values():
            kind = node["kind"]
            nodes_by_kind[kind] = nodes_by_kind.get(kind, 0) + 1
        edges_by_relation: dict[str, int] = {}
        for edge in edges:
            relation = edge["relation"]
            edges_by_relation[relation] = edges_by_relation.get(relation, 0) + 1
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes_by_kind": nodes_by_kind,
            "edges_by_relation": edges_by_relation,
        }
