from __future__ import annotations

import logging
import time
from typing import Any, Callable


class SynchronizationEngine:
    """Synchronizes local changes with the backend when connectivity returns."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.mobile.sync")
        self._queue: list[dict[str, Any]] = []
        self._pushed: list[dict[str, Any]] = []
        self._syncing = False

    def enqueue(self, operation: str, payload: dict[str, Any]) -> str:
        item = {
            "id": f"sync{len(self._queue) + 1}",
            "operation": operation,
            "payload": payload,
            "ts": time.time(),
            "synced": False,
        }
        self._queue.append(item)
        return item["id"]

    def sync(self, push: Callable[[dict[str, Any]], bool] | None = None) -> int:
        if self._syncing:
            return 0
        self._syncing = True
        count = 0
        try:
            remaining: list[dict[str, Any]] = []
            for item in self._queue:
                ok = push(item) if push is not None else True
                if ok:
                    item["synced"] = True
                    self._pushed.append(item)
                    count += 1
                else:
                    remaining.append(item)
            self._queue = remaining
        finally:
            self._syncing = False
        return count

    def pending(self) -> list[dict[str, Any]]:
        return [i for i in self._queue if not i["synced"]]

    def clear(self) -> None:
        self._queue.clear()
        self._pushed.clear()

    def status(self) -> dict[str, Any]:
        return {
            "syncing": self._syncing,
            "pending": len(self.pending()),
            "synced": len(self._pushed),
        }
