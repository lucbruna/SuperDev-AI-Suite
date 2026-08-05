"""Intelligence RAG: retrieval over graph nodes plus analysis documents.

Uses the Architecture Graph module's vector index (text-document API) to serve
context for Q&A and to enrich LLM prompts. Degrades to exact-match fallback
when the graph module is unavailable.
"""
from __future__ import annotations

import threading
from typing import Any


class IntelligenceRAG:
    """Retrieval index built from graph nodes + insight documents."""

    def __init__(self) -> None:
        self._index: Any | None = None
        self._lock = threading.Lock()
        self._documents: dict[str, str] = {}

    def _ensure_index(self) -> Any | None:
        if self._index is not None:
            return self._index
        with self._lock:
            if self._index is None:
                try:
                    from modules.architecture_graph.storage.vector_index import (
                        VectorIndex,
                    )

                    self._index = VectorIndex(dim=512)
                except Exception:
                    self._index = None
            return self._index

    def index_graph(self, graph: Any) -> int:
        index = self._ensure_index()
        count = 0
        for node in graph.nodes():
            text = self._node_text(node)
            self._documents[node.id] = text
            if index is not None:
                index.add(node.id, text)
                count += 1
        return count

    @staticmethod
    def _node_text(node: Any) -> str:
        parts = [
            f"{node.kind} {node.name}",
            f"path: {node.path or ''}",
            f"layer: {node.layer or ''}",
            f"language: {node.language or ''}",
        ]
        meta = getattr(node, "meta", None)
        if isinstance(meta, dict):
            parts.append(f"meta: {meta}")
        return " | ".join(parts)

    def search(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        index = self._ensure_index()
        if index is not None:
            try:
                raw = index.search(query, top_k=limit)
                return [self._normalize(item) for item in raw]
            except Exception:
                pass
        # Exact-match fallback over indexed documents.
        needle = query.lower()
        matches = [
            {"doc_id": doc_id, "score": 0.5, "text": text}
            for doc_id, text in self._documents.items()
            if needle in text.lower()
        ]
        return matches[:limit]

    def _normalize(self, item: Any) -> dict[str, Any]:
        if isinstance(item, dict):
            result = dict(item)
        elif isinstance(item, (tuple, list)) and len(item) == 2:
            result = {"doc_id": item[0], "score": float(item[1])}
        else:
            result = {"doc_id": str(item), "score": 0.0}
        result.setdefault("text", self._documents.get(str(result["doc_id"]), ""))
        return result

    def context(self, query: str, *, limit: int = 5) -> str:
        results = self.search(query, limit=limit)
        if not results:
            return ""
        return "\n".join(
            f"- {r.get('doc_id')}: {r.get('text', '')[:300]}" for r in results
        )

    def stats(self) -> dict[str, Any]:
        return {"documents": len(self._documents), "indexed": self._index is not None}


_rag: IntelligenceRAG | None = None
_rag_lock = threading.Lock()


def get_rag() -> IntelligenceRAG:
    global _rag
    if _rag is None:
        with _rag_lock:
            if _rag is None:
                _rag = IntelligenceRAG()
    return _rag
