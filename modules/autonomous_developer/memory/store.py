"""Persistent JSON-backed memory store for cross-run knowledge."""
from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__all__ = ["MemoryEntry", "MemoryStore"]


@dataclass(slots=True)
class MemoryEntry:
    """A single keyed memory entry with timestamp and tags."""

    key: str
    value: Any
    timestamp: float = field(default_factory=time.time)
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        return cls(
            key=str(data["key"]),
            value=data.get("value"),
            timestamp=float(data.get("timestamp", 0.0)),
            tags=list(data.get("tags", [])),
        )


class MemoryStore:
    """Key/value store persisted atomically to a JSON file.

    Without a backing path the store is in-memory only and ``save`` raises.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._entries: dict[str, MemoryEntry] = {}
        if self.path is not None and self.path.exists():
            self.load()

    def put(
        self, key: str, value: Any, tags: list[str] | None = None
    ) -> MemoryEntry:
        """Store (or overwrite) a value under ``key``."""
        entry = MemoryEntry(key=key, value=value, tags=list(tags or []))
        self._entries[key] = entry
        return entry

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for ``key`` or ``default`` when missing."""
        entry = self._entries.get(key)
        return entry.value if entry is not None else default

    def entry(self, key: str) -> MemoryEntry | None:
        """Return the full entry for ``key``, or ``None`` when missing."""
        return self._entries.get(key)

    def delete(self, key: str) -> bool:
        """Remove ``key``; returns whether it existed."""
        return self._entries.pop(key, None) is not None

    def contains(self, key: str) -> bool:
        return key in self._entries

    def keys(self) -> list[str]:
        return list(self._entries)

    def entries(self) -> list[MemoryEntry]:
        return list(self._entries.values())

    def clear(self) -> None:
        self._entries.clear()

    def stats(self) -> dict[str, Any]:
        return {"count": len(self._entries), "keys": list(self._entries)}

    def save(self) -> None:
        """Atomically persist all entries to the backing JSON file."""
        if self.path is None:
            raise ValueError("MemoryStore has no backing path")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"entries": [entry.to_dict() for entry in self._entries.values()]}
        fd, tmp = tempfile.mkstemp(dir=str(self.path.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def load(self) -> None:
        """Reload entries from the backing file (no-op when absent)."""
        if self.path is None or not self.path.exists():
            return
        with open(self.path, encoding="utf-8") as handle:
            payload = json.load(handle)
        raw = payload.get("entries", []) if isinstance(payload, dict) else payload
        self._entries = {
            str(item["key"]): MemoryEntry.from_dict(item) for item in raw
        }
