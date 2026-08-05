"""RabbitMQ Bridge — queue publish/consume over in-memory queues (no broker)."""
from __future__ import annotations

from collections import deque
from typing import Any


class RabbitMQBridge:
    """Publish/consume to named queues (local)."""

    def __init__(self) -> None:
        self._queues: dict[str, deque[dict[str, Any]]] = {}

    def publish(self, queue: str, message: dict[str, Any]) -> dict[str, Any]:
        self._queues.setdefault(queue, deque(maxlen=1000)).append(message)
        return {"queue": queue, "queued": len(self._queues[queue])}

    def consume(self, queue: str) -> dict[str, Any]:
        q = self._queues.get(queue)
        message = q.popleft() if q else None
        return {"queue": queue, "message": message, "remaining": len(q) if q else 0}


_rabbitmq_bridge: RabbitMQBridge | None = None


def get_rabbitmq_bridge() -> RabbitMQBridge:
    global _rabbitmq_bridge
    if _rabbitmq_bridge is None:
        _rabbitmq_bridge = RabbitMQBridge()
    return _rabbitmq_bridge
