from __future__ import annotations

import logging
from typing import Any

from ..knowledge_interfaces import MemoryStore
from ..knowledge_models import MemoryRecord


class LongTermMemory:
    """Permanent knowledge accumulated across projects and sessions."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.long_term")
        self._store = store
        self._pinned: dict[str, str] = {}

    def commit(self, content: str, importance: float = 0.5, metadata: dict[str, Any] | None = None) -> str:
        if self._store is None:
            raise RuntimeError("long-term memory requires a memory store")
        record = MemoryRecord(
            content=content, memory_type="long_term", importance=importance, metadata=metadata or {},
        )
        return self._store.save(record)

    def recall(self) -> list[MemoryRecord]:
        if self._store is None:
            return []
        records = self._store.list("long_term")
        records.sort(key=lambda r: r.importance, reverse=True)
        return records

    def pin(self, key: str, content: str) -> None:
        self._pinned[key] = content

    def unpin(self, key: str) -> bool:
        return self._pinned.pop(key, None) is not None

    def pinned(self) -> dict[str, str]:
        return dict(self._pinned)

    def summary(self) -> list[str]:
        return [r.content for r in self.recall()[:20]]
