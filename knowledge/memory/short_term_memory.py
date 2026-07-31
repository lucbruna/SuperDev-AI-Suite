from __future__ import annotations

import logging
from collections import OrderedDict
from typing import Any

from ..knowledge_models import MemoryRecord


class ShortTermMemory:
    """Bounded task-scoped memory with LRU eviction.

    Used to hold the context of the current task (e.g. "language=Python,
    database=PostgreSQL, framework=FastAPI").
    """

    def __init__(self, capacity: int = 100) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.short_term")
        self._capacity = capacity
        self._entries: OrderedDict[str, str] = OrderedDict()

    def remember(self, key: str, value: str) -> None:
        self._entries[key] = value
        self._entries.move_to_end(key)
        while len(self._entries) > self._capacity:
            self._entries.popitem(last=False)

    def recall(self, key: str) -> str | None:
        if key in self._entries:
            self._entries.move_to_end(key)
            return self._entries[key]
        return None

    def forget(self, key: str) -> bool:
        return self._entries.pop(key, None) is not None

    def clear(self) -> None:
        self._entries.clear()

    def snapshot(self) -> dict[str, str]:
        return dict(self._entries)

    def size(self) -> int:
        return len(self._entries)

    def all(self) -> list[MemoryRecord]:
        return [
            MemoryRecord(
                content=f"{key}={value}",
                memory_type="short_term",
                metadata={"key": key},
            )
            for key, value in self._entries.items()
        ]
