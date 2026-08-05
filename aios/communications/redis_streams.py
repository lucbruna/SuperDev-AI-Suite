"""AIOS Redis Streams — stream append/read emulation.

Models Redis Streams semantics: monotonic ids (ms-sequence), append,
range reads and length. In-memory; a deployment may bridge to Redis.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


def _next_id(last_ms: int, last_seq: int, now_ms: int) -> str:
    if now_ms > last_ms:
        return f"{now_ms}-0"
    return f"{last_ms}-{last_seq + 1}"


class RedisStreams:
    """In-memory Redis Streams emulation."""

    def __init__(self) -> None:
        self._streams: dict[str, list[dict[str, Any]]] = {}
        self._last: dict[str, tuple[int, int]] = {}

    def xadd(self, stream: str, fields: dict[str, Any], maxlen: int | None = None) -> dict[str, Any]:
        entries = self._streams.setdefault(stream, [])
        last_ms, last_seq = self._last.get(stream, (0, 0))
        entry_id = _next_id(last_ms, last_seq, int(time.time() * 1000))
        ms, seq = (int(part) for part in entry_id.split("-"))
        self._last[stream] = (ms, seq)
        entry = {
            "id": entry_id,
            "fields": fields,
            "stream": stream,
            "record_id": f"x-{uuid.uuid4().hex[:10]}",
        }
        entries.append(entry)
        if maxlen is not None and len(entries) > maxlen:
            self._streams[stream] = entries[-maxlen:]
        return {"ok": True, "id": entry_id}

    def xrange(self, stream: str, start: str = "-", end: str = "+", limit: int = 100) -> list[dict[str, Any]]:
        entries = self._streams.get(stream, [])
        results = []
        for entry in entries:
            eid = entry["id"]
            if start != "-" and eid < start:
                continue
            if end != "+" and eid > end:
                continue
            results.append(entry)
            if len(results) >= limit:
                break
        return results

    def xlen(self, stream: str) -> int:
        return len(self._streams.get(stream, []))

    def xdel(self, stream: str, entry_id: str) -> bool:
        entries = self._streams.get(stream, [])
        before = len(entries)
        self._streams[stream] = [e for e in entries if e["id"] != entry_id]
        return len(self._streams[stream]) < before

    def snapshot(self) -> dict[str, Any]:
        return {
            "streams": sorted(self._streams.keys()),
            "entries": {s: len(e) for s, e in self._streams.items()},
        }
