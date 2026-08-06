"""Knowledge indexer — composite search index + analyzer hook.

Builds a queryable composite index from the graph, the semantic symbol
index and the vector store produced by earlier analyzers, then answers
queries by combining exact symbol lookup with embedding search. Registered
as an ``analyzer`` (gated by ``run_indexing``) so the pipeline index stage
stores ``search_index`` on the context.
"""
from __future__ import annotations

from typing import Any


class KnowledgeIndexer:
    """Composite index over graph / semantic / embedding artifacts."""

    def __init__(self, *, top_k: int = 5) -> None:
        self.top_k = max(1, top_k)

    # ── Analyzer interface (invoked by the pipeline index stage) ──────────
    def index(self, ctx) -> dict[str, Any]:
        """Analyzer hook: build the composite index and store it on the context."""
        if not getattr(ctx.config, "run_indexing", True):
            ctx.record("indexing_skipped", True)
            return {"items": 0, "detail": "indexing disabled"}
        graph = ctx.memory.get("knowledge_graph")
        if not graph:
            return {"items": 0, "detail": "no graph"}
        index = self.build(ctx)
        ctx.memory.put("search_index", index)
        ctx.record("index_items", index["stats"]["nodes"])
        return {"items": index["stats"]["nodes"]}

    # ── Build ─────────────────────────────────────────────────────────────
    def build(self, ctx) -> dict[str, Any]:
        """Assemble the composite index from artifacts already on the context."""
        graph = ctx.memory.get("knowledge_graph") or {"nodes": [], "edges": []}
        by_symbol: dict[str, list[dict[str, Any]]] = {}
        by_kind: dict[str, list[dict[str, Any]]] = {}
        for node in graph.get("nodes", []):
            name = node.get("name", "")
            if name:
                by_symbol.setdefault(name, []).append(node)
            by_kind.setdefault(node.get("kind", "unknown"), []).append(node)

        semantic = ctx.memory.get("semantic_index")
        symbol_lookup: dict[str, list[dict[str, Any]]] = {}
        if semantic is not None and hasattr(semantic, "lookup"):
            for name in by_symbol:
                symbol_lookup[name] = semantic.lookup(name)

        return {
            "project_root": graph.get("project_root", ""),
            "by_symbol": by_symbol,
            "by_kind": by_kind,
            "symbol_lookup": symbol_lookup,
            "vector_store": ctx.memory.get("vector_store"),
            "stats": {
                "nodes": len(graph.get("nodes", [])),
                "symbols": len(by_symbol),
                "kinds": len(by_kind),
            },
        }

    # ── Query ─────────────────────────────────────────────────────────────
    def query(self, text: str, ctx) -> dict[str, Any]:
        """Combine exact symbol hits with vector-search hits for ``text``."""
        index = ctx.memory.get("search_index")
        if not index:
            return {"query": text, "symbols": [], "vectors": [], "count": 0}
        symbols = list(index.get("by_symbol", {}).get(text, []))
        vectors: list[Any] = []
        store = index.get("vector_store")
        if store is not None:
            embeddings = self._embeddings(ctx)
            if embeddings is not None:
                vectors = store.search(embeddings.embedder.embed(text), k=self.top_k)
        return {
            "query": text,
            "symbols": symbols,
            "vectors": vectors,
            "count": len(symbols) + len(vectors),
        }

    @staticmethod
    def _embeddings(ctx):
        """Return the registered embedding service, if any."""
        try:
            return ctx.registry.get("analyzer", "embeddings")
        except Exception:  # noqa: BLE001 — registry access can fail on minimal contexts
            return None
