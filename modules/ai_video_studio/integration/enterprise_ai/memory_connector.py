"""Memory Connector — episodic in-memory store (bounded)."""
from __future__ import annotations

import time
from typing import Any


class MemoryConnector:
    """Short-term episodic memory with recency ordering."""

    def __init__(self, limit: int = 200) -> None:
        self._entries: list[dict[str, Any]] = []
        self._limit = limit

    def store(self, content: str, **meta: Any) -> dict[str, Any]:
        entry = {
            "ts": round(time.time(), 3),
            "content": content,
            **meta,
        }
        self._entries.append(entry)
        if len(self._entries) > self._limit:
            self._entries = self._entries[-self._limit:]
        return {"stored": len(self._entries)}

    def recall(self, query: str, *, limit: int = 5) -> dict[str, Any]:
        q = query.lower()
        scored = [
            (sum(1 for w in q.split() if w in e["content"].lower()), e)
            for e in self._entries
        ]
        hits = [e for score, e in sorted(scored, key=lambda x: (-x[0], -x[1]["ts"])) if score][:limit]
        return {"query": query, "hits": [dict(e) for e in hits], "count": len(hits)}

    def stats(self) -> dict[str, Any]:
        return {"entries": len(self._entries), "limit": self._limit}


_memory_connector: MemoryConnector | None = None


def get_memory_connector() -> MemoryConnector:
    global _memory_connector
    if _memory_connector is None:
        _memory_connector = MemoryConnector()
    return _memory_connector
