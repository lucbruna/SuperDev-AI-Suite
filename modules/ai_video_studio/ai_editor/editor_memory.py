"""Editor memory — bounded LRU cache for frames, previews and computed data."""
from __future__ import annotations

import threading
from collections import OrderedDict
from typing import Any, Hashable

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.memory")


class EditorMemory:
    """Thread-safe LRU cache with a byte-ish size bound (by item count)."""

    def __init__(self, capacity: int = 256) -> None:
        self.capacity = max(1, capacity)
        self._store: OrderedDict[Hashable, Any] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: Hashable) -> Any | None:
        with self._lock:
            if key not in self._store:
                return None
            self._store.move_to_end(key)
            return self._store[key]

    def put(self, key: Hashable, value: Any) -> None:
        with self._lock:
            self._store[key] = value
            self._store.move_to_end(key)
            while len(self._store) > self.capacity:
                self._store.popitem(last=False)

    def get_or_compute(self, key: Hashable, factory: Any) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = factory()
        self.put(key, value)
        return value

    def drop(self, key: Hashable) -> bool:
        with self._lock:
            return self._store.pop(key, None) is not None

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._store)
