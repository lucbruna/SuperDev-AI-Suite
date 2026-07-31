from __future__ import annotations

import time
from typing import Any


class ArchiveEntry:
    """A single archived memory entry."""

    def __init__(self, key: str, value: Any):
        self._key = key
        self._value = value
        self._archived_at = time.time()

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> Any:
        return self._value

    @property
    def archived_at(self) -> float:
        return self._archived_at

    def to_dict(self) -> dict[str, Any]:
        return {"key": self._key, "value": self._value, "archived_at": self._archived_at}


class ArchiveManager:
    """Manages archiving of memory entries for later retrieval."""

    def __init__(self):
        self._archive: dict[str, ArchiveEntry] = {}

    @property
    def archived_count(self) -> int:
        return len(self._archive)

    def archive(self, key: str, value: Any) -> ArchiveEntry:
        entry = ArchiveEntry(key, value)
        self._archive[key] = entry
        return entry

    def archive_batch(self, items: dict[str, Any]) -> int:
        count = 0
        for k, v in items.items():
            self.archive(k, v)
            count += 1
        return count

    def retrieve(self, key: str) -> Any | None:
        entry = self._archive.get(key)
        if entry is None:
            return None
        return entry.value

    def retrieve_entry(self, key: str) -> ArchiveEntry | None:
        return self._archive.get(key)

    def list_archived_keys(self) -> list[str]:
        return list(self._archive.keys())

    def search_archive(self, query: str) -> list[ArchiveEntry]:
        q = query.lower()
        return [e for e in self._archive.values() if q in str(e.value).lower()]

    def remove_archived(self, key: str) -> bool:
        return self._archive.pop(key, None) is not None

    def clear(self) -> None:
        self._archive.clear()
