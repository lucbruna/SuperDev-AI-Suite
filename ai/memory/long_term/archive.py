from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .storage import Storage


class ArchiveEntry:
    """Metadata for an archived entry."""

    def __init__(self, key: str, path: str, size: int, archived_at: float):
        self._key = key
        self._path = path
        self._size = size
        self._archived_at = archived_at

    @property
    def key(self) -> str:
        return self._key

    @property
    def path(self) -> str:
        return self._path

    @property
    def size(self) -> int:
        return self._size

    @property
    def archived_at(self) -> float:
        return self._archived_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self._key,
            "path": self._path,
            "size": self._size,
            "archived_at": self._archived_at,
        }


class Archive:
    """Archive mechanism for rarely-accessed long-term data."""

    def __init__(self, storage: Storage, archive_dir: str | Path | None = None):
        self._storage = storage
        self._archive_dir = Path(archive_dir) if archive_dir else Path.cwd() / ".archive"
        self._entries: dict[str, ArchiveEntry] = {}

    @property
    def count(self) -> int:
        return len(self._entries)

    def archive(self, key: str) -> bool:
        data = self._storage.get(key)
        if data is None:
            return False
        self._archive_dir.mkdir(parents=True, exist_ok=True)
        path = self._archive_dir / f"{key}_{int(time.time())}.archive"
        raw = json.dumps(data, default=str, indent=2)
        path.write_text(raw)
        entry = ArchiveEntry(key, str(path), len(raw.encode("utf-8")), time.time())
        self._entries[key] = entry
        self._storage.delete(key)
        return True

    def restore(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is None:
            return False
        path = Path(entry.path)
        if not path.exists():
            del self._entries[key]
            return False
        data = json.loads(path.read_text())
        self._storage.put(key, data)
        path.unlink()
        del self._entries[key]
        return True

    def list_archived(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._entries.values()]

    def delete_archive(self, key: str) -> bool:
        entry = self._entries.pop(key, None)
        if entry:
            Path(entry.path).unlink(missing_ok=True)
            return True
        return False

    def clear(self) -> None:
        for entry in self._entries.values():
            Path(entry.path).unlink(missing_ok=True)
        self._entries.clear()
