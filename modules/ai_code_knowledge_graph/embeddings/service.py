"""Embedding service — indexes scan/graph content into a vector store.

Registered as an ``analyzer`` so the pipeline index stage embeds file and
entity nodes after the graph builder runs. Search and similarity queries over
the embedded knowledge base back the engine's ``search()`` / RAG features.
"""
from __future__ import annotations

import logging
from typing import Any

from modules.ai_code_knowledge_graph.embeddings.embedder import Embedder, HashEmbedder
from modules.ai_code_knowledge_graph.embeddings.vector_store import MemoryVectorStore, VectorStore

logger = logging.getLogger(__name__)

_DEFINITION_KINDS = frozenset(
    {"class", "function", "method", "interface", "type", "enum", "table", "view", "plugin", "workflow"}
)


class EmbeddingService:
    """Embeds knowledge content and answers similarity/search queries."""

    def __init__(
        self,
        embedder: Embedder | None = None,
        store: VectorStore | None = None,
        *,
        enabled: bool = True,
    ) -> None:
        self.embedder = embedder or HashEmbedder()
        self.store = store or MemoryVectorStore()
        self.enabled = enabled

    # ── Analyzer interface (invoked by the pipeline index stage) ──────────
    def index(self, ctx) -> dict[str, Any]:
        """Analyzer hook: embed files/entities and store the vector store."""
        if not getattr(ctx.config, "run_embeddings", True) or not self.enabled:
            ctx.record("embeddings_skipped", True)
            return {"items": 0, "detail": "embeddings disabled"}
        scan_result = ctx.memory.get("scan_result")
        graph = ctx.memory.get("knowledge_graph")
        if not scan_result:
            return {"items": 0, "detail": "no scan result"}
        self.index_scan(scan_result, graph)
        ctx.memory.put("vector_store", self.store)
        ctx.record("embeddings_items", self.store.size())
        return {"items": self.store.size()}

    # ── Indexing ──────────────────────────────────────────────────────────
    def index_scan(self, scan_result: dict[str, Any], graph: dict[str, Any] | None = None) -> int:
        """Embed every file and definition entity from the scan (and graph)."""
        count = 0
        for entry in scan_result.get("files", []):
            rel_path = entry.get("rel_path")
            if not rel_path:
                continue
            blob = self._file_blob(entry)
            self.store.add(f"file:{rel_path}", self.embedder.embed(blob), {"kind": "file", "file": rel_path})
            count += 1

        nodes = (graph or {}).get("nodes", [])
        for node in nodes:
            kind = node.get("kind")
            if kind not in _DEFINITION_KINDS:
                continue
            name = node.get("name", "")
            blob = f"{kind} {name} {node.get('file', '')}"
            self.store.add(node.get("id", ""), self.embedder.embed(blob), {"kind": kind, "name": name, "file": node.get("file", "")})
            count += 1
        logger.debug("Embedded %d items", count)
        return count

    # ── Queries ───────────────────────────────────────────────────────────
    def search(self, query: str, k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        """Return top-k embedded items most similar to the query."""
        return self.store.search(self.embedder.embed(query), k=max(0, k))

    def similar(self, item_id: str, k: int = 5) -> list[tuple[str, float, dict[str, Any]]]:
        """Return items most similar to an already-indexed item."""
        if isinstance(self.store, MemoryVectorStore):
            found = self.store.get(item_id)
            if found:
                return self.store.search(found[0], k=max(0, k))
        return []

    # ── Helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def _file_blob(entry: dict[str, Any]) -> str:
        """Build a searchable text blob for a scanned file."""
        parts = [entry.get("rel_path", ""), entry.get("language", "")]
        parsed = entry.get("parsed")
        if isinstance(parsed, dict):
            for entity in parsed.get("entities", [])[:200]:
                parts.append(f"{entity.get('kind', '')} {entity.get('name', '')}")
        return "\n".join(part for part in parts if part)
