"""Redis Streams — local topic queues with a redis-like API (no server needed)."""
from __future__ import annotations

from collections import deque
from typing import Any


class RedisStreamsBridge:
    """In-memory stream with XADD-style appends and range reads."""

    def __init__(self) -> None:
        self._streams: dict[str, deque[dict[str, Any]]] = {}
        self._seq = 0

    def add(self, stream: str, fields: dict[str, Any]) -> dict[str, Any]:
        self._seq += 1
        entry = {"id": f"{self._seq}-0", **fields}
        self._streams.setdefault(stream, deque(maxlen=1000)).append(entry)
        return {"stream": stream, "entry_id": entry["id"]}

    def read(self, stream: str, *, count: int = 10) -> dict[str, Any]:
        entries = list(self._streams.get(stream, deque()))[-count:]
        return {"stream": stream, "entries": entries, "count": len(entries)}


_redis_streams: RedisStreamsBridge | None = None


def get_redis_streams() -> RedisStreamsBridge:
    global _redis_streams
    if _redis_streams is None:
        _redis_streams = RedisStreamsBridge()
    return _redis_streams
