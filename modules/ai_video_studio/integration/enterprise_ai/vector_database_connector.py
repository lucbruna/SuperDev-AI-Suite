"""Vector Database Connector — in-memory vector index with cosine search."""
from __future__ import annotations

import math
from typing import Any

from modules.ai_video_studio.integration.enterprise_ai.embeddings_connector import (
    get_embeddings_connector,
)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class VectorDatabaseConnector:
    """Small in-memory vector store with cosine similarity search."""

    def __init__(self) -> None:
        self._items: list[dict[str, Any]] = []

    def upsert(self, text: str, *, id: str | None = None, **meta: Any) -> dict[str, Any]:
        vec = get_embeddings_connector().embed(text)["vector"]
        item = {"id": id or f"vec_{len(self._items) + 1}", "text": text, "vector": vec, **meta}
        self._items = [i for i in self._items if i["id"] != item["id"]]
        self._items.append(item)
        return {"id": item["id"], "indexed": len(self._items)}

    def search(self, query: str, *, top_k: int = 5) -> dict[str, Any]:
        qv = get_embeddings_connector().embed(query)["vector"]
        scored = sorted(
            ({"id": i["id"], "text": i["text"], "score": round(_cosine(qv, i["vector"]), 4)}
             for i in self._items),
            key=lambda x: -x["score"],
        )[:top_k]
        return {"query": query, "results": scored, "count": len(scored)}

    def stats(self) -> dict[str, Any]:
        return {"indexed": len(self._items)}


_vector_database_connector: VectorDatabaseConnector | None = None


def get_vector_database_connector() -> VectorDatabaseConnector:
    global _vector_database_connector
    if _vector_database_connector is None:
        _vector_database_connector = VectorDatabaseConnector()
    return _vector_database_connector
