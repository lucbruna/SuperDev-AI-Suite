from __future__ import annotations

import logging
from typing import Any, Callable

from .queue_models import QueueItem, QueueStatus
from .queue_priority import QueuePriority
from .queue_persistence import QueuePersistence


class QueueManager:
    """Manages queue lifecycle including persistence and priority."""

    def __init__(self) -> None:
        self._items: list[QueueItem] = []
        self._priority = QueuePriority()
        self._persistence = QueuePersistence()
        self._log = logging.getLogger("superdev.workflow.queues.manager")

    def add(self, item: QueueItem) -> None:
        self._items.append(item)
        self._persistence.save(item)

    def get_next(self) -> QueueItem | None:
        return self._priority.highest(self._items)

    def ack(self, item_id: str) -> None:
        for item in self._items:
            if item.id == item_id:
                item.status = QueueStatus.COMPLETED
                self._persistence.save(item)
                break

    def nack(self, item_id: str, error: str) -> None:
        for item in self._items:
            if item.id == item_id:
                if item.retries < item.max_retries:
                    item.retries += 1
                    item.status = QueueStatus.RETRYING
                else:
                    item.status = QueueStatus.FAILED
                    item.error = error
                self._persistence.save(item)
                break

    @property
    def size(self) -> int:
        return len(self._items)
