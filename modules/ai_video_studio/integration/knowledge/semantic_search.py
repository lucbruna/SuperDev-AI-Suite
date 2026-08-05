"""Semantic Search — ranked retrieval over indexed documents."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.enterprise_ai.embeddings_connector import (
    get_embeddings_connector,
)


class SemanticSearch:
    """Cosine-similarity search over an in-memory document store."""

    def __init__(self) -> None:
        self._docs: list[dict[str, Any]] = []

    def index(self, text: str, *, id: str | None = None, **meta: Any) -> dict[str, Any]:
        vec = get_embeddings_connector().embed(text)["vector"]
        doc = {"id": id or f"doc_{len(self._docs) + 1}", "text": text, "vector": vec, **meta}
        self._docs = [d for d in self._docs if d["id"] != doc["id"]]
        self._docs.append(doc)
        return {"indexed": len(self._docs), "id": doc["id"]}

    def search(self, query: str, *, top_k: int = 5) -> dict[str, Any]:
        qv = get_embeddings_connector().embed(query)["vector"]

        def _cos(a: list[float], b: list[float]) -> float:
            return sum(x * y for x, y in zip(a, b, strict=False))

        scored = sorted(
            ({"id": d["id"], "text": d["text"], "score": round(_cos(qv, d["vector"]), 4)}
             for d in self._docs),
            key=lambda x: -x["score"],
        )[:top_k]
        return {"query": query, "results": scored, "count": len(scored)}

    def stats(self) -> dict[str, Any]:
        return {"indexed": len(self._docs)}


_semantic_search: SemanticSearch | None = None


def get_semantic_search() -> SemanticSearch:
    global _semantic_search
    if _semantic_search is None:
        _semantic_search = SemanticSearch()
    return _semantic_search
