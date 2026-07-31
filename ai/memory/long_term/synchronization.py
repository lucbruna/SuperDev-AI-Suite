from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class SyncEntry:
    """A single synchronization entry."""

    def __init__(self, key: str, action: str, data: Any | None = None):
        self._key = key
        self._action = action
        self._data = data
        self._timestamp = time.time()
        self._synced: bool = False

    @property
    def key(self) -> str:
        return self._key

    @property
    def action(self) -> str:
        return self._action

    @property
    def data(self) -> Any | None:
        return self._data

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def synced(self) -> bool:
        return self._synced

    def mark_synced(self) -> None:
        self._synced = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self._key,
            "action": self._action,
            "timestamp": self._timestamp,
            "synced": self._synced,
        }


class Synchronization:
    """Synchronization between memory layers."""

    def __init__(self):
        self._queue: list[SyncEntry] = []
        self._handlers: dict[str, Callable] = {}

    @property
    def queue_size(self) -> int:
        return len(self._queue)

    def register_handler(self, action: str, handler: Callable) -> None:
        self._handlers[action] = handler

    def enqueue(self, key: str, action: str, data: Any = None) -> SyncEntry:
        entry = SyncEntry(key, action, data)
        self._queue.append(entry)
        return entry

    def sync(self) -> int:
        count = 0
        for entry in self._queue:
            if entry.synced:
                continue
            handler = self._handlers.get(entry.action)
            if handler:
                try:
                    handler(entry.key, entry.data)
                    entry.mark_synced()
                    count += 1
                except Exception:
                    pass
        self._queue = [e for e in self._queue if not e.synced]
        return count

    def sync_key(self, key: str) -> bool:
        for entry in self._queue:
            if entry.key == key and not entry.synced:
                handler = self._handlers.get(entry.action)
                if handler:
                    try:
                        handler(entry.key, entry.data)
                        entry.mark_synced()
                        return True
                    except Exception:
                        return False
        return False

    def pending_entries(self) -> list[SyncEntry]:
        return [e for e in self._queue if not e.synced]

    def clear(self) -> None:
        self._queue.clear()
