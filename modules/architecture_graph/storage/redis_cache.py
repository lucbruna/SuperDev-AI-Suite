"""Optional Redis cache for rendered graph payloads.

Graceful degradation: when the ``redis`` package is unavailable or the server
is unreachable, the cache behaves as a no-op so the module still works.
"""
from __future__ import annotations

import json
import threading
from typing import Any

from modules.architecture_graph.config.graph_settings import get_settings


class RedisCache:
    """JSON-value cache over Redis with a process-level fallback."""

    prefix = "superdev:architecture-graph:"

    def __init__(self, url: str = "", *, enabled: bool = True) -> None:
        self._fallback: dict[str, tuple[float, str]] = {}
        self._lock = threading.Lock()
        self._client: Any | None = None
        if not enabled:
            return
        if not url:
            url = get_settings().config.redis_url
        if not url:
            return
        try:
            from redis import Redis

            self._client = Redis.from_url(url, decode_responses=True, socket_connect_timeout=2)
        except ImportError:
            self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def get(self, key: str) -> Any | None:
        full = self.prefix + key
        if self._client is not None:
            try:
                raw = self._client.get(full)
                return json.loads(raw) if raw else None
            except Exception:
                return None
        with self._lock:
            item = self._fallback.get(full)
        if item is None:
            return None
        import time

        if item[0] < time.monotonic():
            with self._lock:
                self._fallback.pop(full, None)
            return None
        return json.loads(item[1])

    def set(self, key: str, value: Any, ttl: int = 120) -> None:
        full = self.prefix + key
        payload = json.dumps(value, ensure_ascii=False)
        if self._client is not None:
            try:
                self._client.set(full, payload, ex=ttl)
                return
            except Exception:
                pass
        import time

        with self._lock:
            self._fallback[full] = (time.monotonic() + ttl, payload)

    def invalidate(self, pattern: str = "*") -> None:
        if self._client is not None:
            try:
                keys = self._client.keys(self.prefix + pattern)
                if keys:
                    self._client.delete(*keys)
                return
            except Exception:
                pass
        with self._lock:
            self._fallback.clear()
