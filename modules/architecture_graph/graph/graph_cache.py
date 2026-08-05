"""Caching for serialized graph views and incremental scan snapshots.

Two concerns live here:
* an LRU cache of rendered payloads (reactflow/mermaid/json/...) keyed by
  (format, filters, graph built_at) so repeated dashboard calls are cheap;
* the file snapshot used by the discovery engine to detect changes between
  scans (stored as JSON in the module data directory).
"""
from __future__ import annotations

import json
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any

from modules.architecture_graph.config.graph_settings import get_settings


class LRUCache:
    """Thread-safe least-recently-used string-keyed cache."""

    def __init__(self, capacity: int = 64) -> None:
        self.capacity = max(1, capacity)
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            self._store.move_to_end(key)
            return item[1]

    def set(self, key: str, value: Any, ttl: float = 60.0) -> None:
        with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)
            self._store.move_to_end(key)
            while len(self._store) > self.capacity:
                self._store.popitem(last=False)

    def invalidate(self) -> None:
        with self._lock:
            self._store.clear()

    def _purge(self) -> None:
        now = time.monotonic()
        expired = [k for k, (exp, _) in self._store.items() if exp < now]
        for key in expired:
            self._store.pop(key, None)


class GraphCache:
    """Process-level cache for rendered graph views keyed by built_at."""

    def __init__(self, capacity: int = 64) -> None:
        self._cache = LRUCache(capacity)
        self._lock = threading.Lock()

    def key_for(self, fmt: str, built_at: str, extra: str = "") -> str:
        return f"{fmt}|{built_at}|{extra}"

    def get(self, fmt: str, built_at: str, extra: str = "") -> Any | None:
        return self._cache.get(self.key_for(fmt, built_at, extra))

    def set(self, fmt: str, built_at: str, payload: Any, extra: str = "", ttl: float = 120.0) -> None:
        self._cache.set(self.key_for(fmt, built_at, extra), payload, ttl=ttl)

    def invalidate(self) -> None:
        self._cache.invalidate()


# ---------------------------------------------------------------------------
# File snapshot (discovery engine support)
# ---------------------------------------------------------------------------

def snapshot_path() -> Path:
    return Path(get_settings().config.snapshot_path)


def load_snapshot() -> dict[str, Any] | None:
    path = snapshot_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def save_snapshot(data: dict[str, Any]) -> None:
    path = snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
    )
