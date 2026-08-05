"""AIOS Enterprise Memory Engine — facade over all memory stores.

The engine owns a registry of named stores (episodic, semantic,
procedural, working, conversation, knowledge, vector, cache) and
exposes a uniform store/recall contract.
"""

from __future__ import annotations

from typing import Any

from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory
from .procedural_memory import ProceduralMemory
from .working_memory import WorkingMemory
from .conversation_memory import ConversationMemory
from .knowledge_memory import KnowledgeMemory
from .vector_memory import VectorMemory
from .cache_memory import CacheMemory

DEFAULT_KINDS = (
    "episodic",
    "semantic",
    "procedural",
    "working",
    "conversation",
    "knowledge",
    "vector",
    "cache",
)


class MemoryEngine:
    """Composes the platform memory stores under one API."""

    def __init__(self) -> None:
        self._stores: dict[str, Any] = {}
        self.register("episodic", EpisodicMemory())
        self.register("semantic", SemanticMemory())
        self.register("procedural", ProceduralMemory())
        self.register("working", WorkingMemory())
        self.register("conversation", ConversationMemory())
        self.register("knowledge", KnowledgeMemory())
        self.register("vector", VectorMemory())
        self.register("cache", CacheMemory())

    def register(self, kind: str, store: Any) -> "MemoryEngine":
        self._stores[kind] = store
        return self

    def get(self, kind: str, default: Any = None) -> Any:
        return self._stores.get(kind, default)

    def kinds(self) -> list[str]:
        return sorted(self._stores)

    # -- uniform operations ---------------------------------------------
    def store(self, kind: str, content: Any, **meta: Any) -> dict[str, Any]:
        store = self._stores.get(kind)
        if store is None:
            return {"ok": False, "error": f"unknown memory kind: {kind}", "store": kind}
        try:
            record = store.store(content, **meta)
            return {"ok": True, "store": kind, "record": record}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "store": kind, "error": f"{type(exc).__name__}: {exc}"}

    def recall(self, kind: str, query: Any = None, limit: int = 5, **filters: Any) -> dict[str, Any]:
        store = self._stores.get(kind)
        if store is None:
            return {"ok": False, "error": f"unknown memory kind: {kind}", "store": kind}
        try:
            results = store.recall(query=query, limit=limit, **filters)
            return {"ok": True, "store": kind, "count": len(results), "results": results}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "store": kind, "error": f"{type(exc).__name__}: {exc}"}

    def forget(self, kind: str, record_id: str) -> dict[str, Any]:
        store = self._stores.get(kind)
        if store is None:
            return {"ok": False, "error": f"unknown memory kind: {kind}"}
        return {"ok": True, "store": kind, "forgotten": store.forget(record_id)}

    def clear(self, kind: str | None = None) -> dict[str, Any]:
        kinds = [kind] if kind is not None else list(self._stores)
        if kind is not None and kind not in self._stores:
            return {"ok": False, "error": f"unknown memory kind: {kind}"}
        cleared = []
        for k in kinds:
            self._stores[k].clear()
            cleared.append(k)
        return {"ok": True, "cleared": cleared}

    def stats(self) -> dict[str, Any]:
        return {kind: store.stats() for kind, store in sorted(self._stores.items())}

    def snapshot(self) -> dict[str, Any]:
        return {
            "kinds": self.kinds(),
            "stores": {kind: store.snapshot() for kind, store in sorted(self._stores.items())},
        }
