"""Retrieval-Augmented Generation over the architecture graph.

Indexes graph nodes (files, modules, APIs, agents, plugins, workflows) into a
sparse vector space and provides ranked retrieval for natural-language
questions about the codebase. Built on the module's :class:`VectorIndex`, it
works fully offline with zero hard dependencies.
"""
from __future__ import annotations

import threading
from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.storage.vector_index import VectorIndex


class ArchitectureRAG:
    """Sparse-vector retrieval over architecture nodes."""

    def __init__(self, dim: int = 512) -> None:
        self.index = VectorIndex(dim=dim)
        self._nodes: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------- indexing
    def index_graph(self, graph: ArchitectureGraph) -> int:
        """Index every node of the graph. Returns the number of indexed nodes."""
        with self._lock:
            self.index.clear()
            self._nodes.clear()
            count = 0
            for node in graph.nodes():
                text = self._node_text(node)
                if not text.strip():
                    continue
                self.index.add(node.id, text)
                self._nodes[node.id] = node.to_dict()
                count += 1
            return count

    def index_node(self, node_id: str, text: str) -> None:
        """Add or refresh a single node document."""
        with self._lock:
            self.index.add(node_id, text)

    def remove_node(self, node_id: str) -> None:
        # VectorIndex has no remove; re-indexing replaces the whole graph.
        with self._lock:
            self._nodes.pop(node_id, None)

    @staticmethod
    def _node_text(node: Any) -> str:
        parts = [
            node.name,
            node.kind,
            node.language,
            node.path,
            node.layer,
            " ".join(
                f"{k}:{v}"
                for k, v in node.meta.items()
                if not isinstance(v, (dict, list))
            ),
        ]
        return " ".join(p for p in parts if p)

    # ------------------------------------------------------------ retrieval
    def search(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        """Ranked node results for a text query."""
        scored = self.index.search(query, top_k=limit)
        results: list[dict[str, Any]] = []
        for node_id, score in scored:
            node = self._nodes.get(node_id)
            if node is None:
                continue
            results.append(
                {"node": node, "score": round(float(score), 4), "node_id": node_id}
            )
        return results

    def context(self, query: str, *, limit: int = 5) -> str:
        """Compact text context for an LLM prompt."""
        hits = self.search(query, limit=limit)
        if not hits:
            return "No architecture context found."
        lines = ["Architecture context (ranked):"]
        for i, hit in enumerate(hits, 1):
            node = hit["node"]
            lines.append(
                f"{i}. {node['kind']} {node['id']} "
                f"(layer={node.get('layer', '') or '?'}, score={hit['score']})"
            )
        return "\n".join(lines)

    def suggest_related(self, node_id: str, *, limit: int = 5) -> list[dict[str, Any]]:
        """Find nodes most similar to a given node id."""
        scored = self.index.similar_to(node_id, top_k=limit)
        results: list[dict[str, Any]] = []
        for nid, score in scored:
            node = self._nodes.get(nid)
            if node is not None:
                results.append({"node": node, "score": round(float(score), 4)})
        return results

    # -------------------------------------------------------------- metrics
    def stats(self) -> dict[str, Any]:
        return {
            "indexed_nodes": len(self._nodes),
            "dim": self.index.dim,
            "provider": "local",
        }


_rag: ArchitectureRAG | None = None
_rag_lock = threading.Lock()


def get_rag() -> ArchitectureRAG:
    """Process-wide singleton RAG service."""
    global _rag
    if _rag is None:
        with _rag_lock:
            if _rag is None:
                _rag = ArchitectureRAG()
    return _rag
