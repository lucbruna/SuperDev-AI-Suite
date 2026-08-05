"""AIOS Episodic Memory — ordered records of past events.

Stores event-like experiences with a timestamp and optional tags;
recall filters by tags and/or keyword matching on a searchable field.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class EpisodicMemory:
    """Append-only store of episodic records."""

    def __init__(self, max_records: int = 10_000) -> None:
        self._records: list[dict[str, Any]] = []
        self._max = max_records

    def store(self, content: Any, **meta: Any) -> dict[str, Any]:
        record = {
            "record_id": f"epi-{uuid.uuid4().hex[:10]}",
            "content": content,
            "tags": list(meta.pop("tags", [])),
            "timestamp": time.time(),
            "meta": meta,
        }
        self._records.append(record)
        if len(self._records) > self._max:
            self._records = self._records[-self._max:]
        return record

    def recall(self, query: Any = None, limit: int = 5, **filters: Any) -> list[dict[str, Any]]:
        tags = set(filters.get("tags", []))
        after = filters.get("after")
        before = filters.get("before")
        query_str = str(query).lower() if query is not None else ""
        matches = []
        for record in reversed(self._records):
            if tags and not tags.issubset(set(record["tags"])):
                continue
            if after is not None and record["timestamp"] < after:
                continue
            if before is not None and record["timestamp"] > before:
                continue
            if query_str and query_str not in str(record.get("content", "")).lower():
                continue
            matches.append(record)
            if len(matches) >= limit:
                break
        return matches

    def forget(self, record_id: str) -> bool:
        before = len(self._records)
        self._records = [r for r in self._records if r["record_id"] != record_id]
        return len(self._records) < before

    def clear(self) -> None:
        self._records.clear()

    def stats(self) -> dict[str, Any]:
        return {"records": len(self._records), "max": self._max}

    def snapshot(self) -> dict[str, Any]:
        return {"records": len(self._records), "max": self._max}
