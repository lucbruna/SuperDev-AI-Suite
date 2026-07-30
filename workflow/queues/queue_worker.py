from __future__ import annotations

import logging
from typing import Any, Callable

from .queue_models import QueueItem, QueueStatus


class QueueWorker:
    """Processes queue items by invoking registered handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._log = logging.getLogger("superdev.workflow.queues.worker")

    def register(self, action: str, handler: Callable[..., Any]) -> None:
        self._handlers[action] = handler

    def process(self, item: QueueItem) -> Any | None:
        action = item.payload.get("action", "")
        handler = self._handlers.get(action)
        if not handler:
            self._log.warning("No handler for action %s", action)
            return None
        try:
            return handler(**item.payload.get("args", {}))
        except Exception as exc:
            self._log.exception("Handler failed for %s", item.id)
            raise
