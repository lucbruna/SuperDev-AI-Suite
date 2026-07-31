from __future__ import annotations

from typing import Any


class GarbageCollector:
    """Collects and removes garbage entries from memory."""

    def __init__(self):
        self._collected_count: int = 0
        self._collection_log: list[str] = []

    @property
    def collected_count(self) -> int:
        return self._collected_count

    @property
    def collection_log(self) -> list[str]:
        return list(self._collection_log)

    def collect(self, entries: dict[str, Any], predicate: Any = None) -> dict[str, Any]:
        if predicate is None:

            def predicate(k, v):
                return v.get("active", True) is False

        kept: dict[str, Any] = {}
        removed: list[str] = []
        for k, v in entries.items():
            if predicate(k, v):
                removed.append(k)
                self._collected_count += 1
            else:
                kept[k] = v
        self._collection_log.extend(removed)
        return kept

    def collect_empty(self, entries: dict[str, Any]) -> dict[str, Any]:
        return self.collect(entries, lambda k, v: not v)

    def collect_by_age(self, entries: dict[str, Any], max_age: float) -> dict[str, Any]:
        import time

        now = time.time()
        return self.collect(entries, lambda k, v: now - v.get("created_at", now) > max_age)

    def stats(self) -> dict[str, Any]:
        return {
            "collected_count": self._collected_count,
            "recent_removals": self._collection_log[-10:],
        }

    def clear(self) -> None:
        self._collected_count = 0
        self._collection_log.clear()
