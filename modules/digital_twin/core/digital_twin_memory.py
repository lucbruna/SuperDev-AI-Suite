"""Persistent memory for the Digital Twin module.

Stores observations as keyed entries persisted atomically to JSON. Kept
deterministic and dependency-free, mirroring the AD memory store pattern.
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


class TwinMemoryError(RuntimeError):
    """Raised on memory persistence failures."""


@dataclass(slots=True)
class TwinMemory:
    """Ordered keyed memory with optional JSON persistence."""

    max_entries: int = 1000
    _entries: dict[str, object] = field(default_factory=dict)

    def remember(self, key: str, value: object) -> None:
        # Move to end to keep insertion order == recency.
        if key in self._entries:
            del self._entries[key]
        self._entries[key] = value
        while len(self._entries) > self.max_entries:
            oldest = next(iter(self._entries))
            del self._entries[oldest]

    def recall(self, key: str, default: object = None) -> object:
        if key not in self._entries:
            return default
        # LRU touch: move to end so insertion order stays recency-ordered.
        value = self._entries.pop(key)
        self._entries[key] = value
        return value

    def forget(self, key: str) -> bool:
        return self._entries.pop(key, None) is not None

    def has(self, key: str) -> bool:
        return key in self._entries

    def keys(self) -> list[str]:
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def to_dict(self) -> dict[str, object]:
        return dict(self._entries)

    def load_dict(self, values: dict[str, object]) -> None:
        self._entries = dict(values)

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(target.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(self._entries, handle, ensure_ascii=False, indent=2)
            os.replace(tmp, target)
        except OSError as exc:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise TwinMemoryError(f"failed to save memory: {exc}") from exc

    @classmethod
    def load(cls, path: str | Path) -> "TwinMemory":
        target = Path(path)
        if not target.exists():
            return cls()
        try:
            with target.open("r", encoding="utf-8") as handle:
                values = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise TwinMemoryError(f"failed to load memory: {exc}") from exc
        memory = cls()
        if isinstance(values, dict):
            memory.load_dict(values)
        return memory
