from __future__ import annotations

import logging
from typing import Any, Callable

from .queue_models import QueueItem, QueueStatus


class QueueEngine:
    """Central queue engine coordinating enqueue/dequeue lifecycle."""

    def __init__(self) -> None:
        self._items: list[QueueItem] = []
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._log = logging.getLogger("superdev.workflow.queues")

    def register_handler(self, action: str, handler: Callable[..., Any]) -> None:
        self._handlers[action] = handler

    def enqueue(self, payload: dict[str, Any], priority: int = 0) -> QueueItem:
        item = QueueItem(payload=payload, priority=priority)
        self._items.append(item)
        self._items.sort(key=lambda x: (-x.priority, x.created_at))
        self._log.info("Enqueued %s", item.id)
        return item

    def dequeue(self) -> QueueItem | None:
        for item in self._items:
            if item.status == QueueStatus.PENDING:
                item.status = QueueStatus.PROCESSING
                return item
        return None

    def complete(self, item_id: str) -> None:
        for item in self._items:
            if item.id == item_id:
                item.status = QueueStatus.COMPLETED
                break

    def fail(self, item_id: str, error: str) -> None:
        for item in self._items:
            if item.id == item_id:
                if item.retries < item.max_retries:
                    item.retries += 1
                    item.status = QueueStatus.RETRYING
                else:
                    item.status = QueueStatus.FAILED
                    item.error = error
                break

    @property
    def pending_count(self) -> int:
        return sum(1 for i in self._items if i.status == QueueStatus.PENDING)
