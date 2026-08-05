"""AIOS Kafka Bridge — topic log emulation with offsets.

Models a Kafka-like append-only log per topic with consumer groups and
per-group offsets. In-memory; a deployment may bridge to real Kafka.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class KafkaBridge:
    """In-memory Kafka-style topic log with consumer groups."""

    def __init__(self) -> None:
        self._topics: dict[str, list[dict[str, Any]]] = {}
        self._offsets: dict[tuple[str, str], int] = {}  # (topic, group) -> next offset

    def create_topic(self, topic: str) -> None:
        self._topics.setdefault(topic, [])

    def produce(self, topic: str, value: Any, key: str | None = None) -> dict[str, Any]:
        log = self._topics.setdefault(topic, [])
        record = {
            "offset": len(log),
            "key": key,
            "value": value,
            "topic": topic,
            "timestamp": time.time(),
            "record_id": f"kfk-{uuid.uuid4().hex[:10]}",
        }
        log.append(record)
        return {"ok": True, **record}

    def consume(self, topic: str, group: str, limit: int = 10) -> list[dict[str, Any]]:
        log = self._topics.get(topic, [])
        start = self._offsets.get((topic, group), 0)
        batch = log[start : start + limit]
        self._offsets[(topic, group)] = start + len(batch)
        return batch

    def commit_offset(self, topic: str, group: str, offset: int) -> None:
        self._offsets[(topic, group)] = max(0, offset)

    def topic_offsets(self, topic: str) -> dict[str, Any]:
        log = self._topics.get(topic, [])
        return {"start": 0, "end": len(log), "count": len(log)}

    def snapshot(self) -> dict[str, Any]:
        return {
            "topics": sorted(self._topics.keys()),
            "groups": sorted({f"{t}/{g}" for t, g in self._offsets}),
            "message_count": sum(len(v) for v in self._topics.values()),
        }
