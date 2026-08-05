"""Kafka Bridge — topic producer/consumer API over an in-memory bus (no broker)."""
from __future__ import annotations

from collections import deque
from typing import Any


class KafkaBridge:
    """Produce/consume to named topics (local ring buffers)."""

    def __init__(self) -> None:
        self._topics: dict[str, deque[dict[str, Any]]] = {}

    def produce(self, topic: str, message: dict[str, Any]) -> dict[str, Any]:
        self._topics.setdefault(topic, deque(maxlen=1000)).append(message)
        return {"topic": topic, "produced": len(self._topics[topic])}

    def consume(self, topic: str, *, count: int = 10) -> dict[str, Any]:
        entries = list(self._topics.get(topic, deque()))[-count:]
        return {"topic": topic, "messages": entries, "count": len(entries)}

    def topics(self) -> dict[str, Any]:
        return {"topics": {t: len(q) for t, q in self._topics.items()}}


_kafka_bridge: KafkaBridge | None = None


def get_kafka_bridge() -> KafkaBridge:
    global _kafka_bridge
    if _kafka_bridge is None:
        _kafka_bridge = KafkaBridge()
    return _kafka_bridge
