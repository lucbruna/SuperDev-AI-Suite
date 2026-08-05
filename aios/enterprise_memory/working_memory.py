"""AIOS Working Memory — transient session state.

Short-lived key/value state per session with TTL and entry limits;
used for scratch data during a run.
"""

from __future__ import annotations

import threading
import time
from typing import Any


class WorkingMemory:
    """Per-session scratch state with TTL."""

    def __init__(self, default_ttl: float = 300.0, max_keys_per_session: int = 200) -> None:
        self._default_ttl = default_ttl
        self._max_keys = max_keys_per_session
        self._state: dict[str, dict[str, tuple[float, Any]]] = {}
        self._lock = threading.Lock()

    def _prune(self, session_id: str, now: float) -> None:
        bucket = self._state.get(session_id)
        if bucket is None:
            return
        expired = [k for k, (exp, _) in bucket.items() if exp < now]
        for key in expired:
            del bucket[key]

    def store(self, content: Any, **meta: Any) -> dict[str, Any]:
        session_id = meta.get("session_id", "default")
        key = meta.get("key")
        if key is None:
            raise ValueError("working store requires meta 'key'")
        ttl = float(meta.get("ttl", self._default_ttl))
        with self._lock:
            now = time.time()
            bucket = self._state.setdefault(session_id, {})
            self._prune(session_id, now)
            bucket[key] = (now + ttl, content)
            if len(bucket) > self._max_keys:
                oldest = min(bucket, key=lambda k: bucket[k][0])
                del bucket[oldest]
        return {"record_id": f"{session_id}:{key}", "key": key, "session_id": session_id}

    def recall(self, query: Any = None, limit: int = 5, **filters: Any) -> list[dict[str, Any]]:
        session_id = filters.get("session_id", "default")
        key = filters.get("key")
        with self._lock:
            bucket = self._state.get(session_id, {})
            self._prune(session_id, time.time())
            items = []
            for k, (exp, value) in bucket.items():
                if key is not None and k != key:
                    continue
                if query is not None and str(query).lower() not in str(value).lower():
                    continue
                items.append({"key": k, "value": value, "expires_at": exp})
                if len(items) >= limit:
                    break
        return items

    def forget(self, record_id: str) -> bool:
        session_id, _, key = record_id.partition(":")
        with self._lock:
            bucket = self._state.get(session_id)
            if bucket and key in bucket:
                del bucket[key]
                return True
        return False

    def clear(self) -> None:
        with self._lock:
            self._state.clear()

    def stats(self) -> dict[str, Any]:
        with self._lock:
            total = sum(len(b) for b in self._state.values())
            return {"sessions": len(self._state), "keys": total, "max_keys_per_session": self._max_keys}

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "sessions": sorted(self._state.keys()),
                "keys": sum(len(b) for b in self._state.values()),
            }
