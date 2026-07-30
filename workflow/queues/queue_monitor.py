from __future__ import annotations

import logging
from typing import Any

from .queue_models import QueueItem, QueueStatus


class QueueMonitor:
    """Monitors queue health and metrics."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.queues.monitor")

    def status_report(self, items: list[QueueItem]) -> dict[str, Any]:
        total = len(items)
        by_status: dict[str, int] = {}
        for s in QueueStatus:
            by_status[s.value] = sum(1 for i in items if i.status == s)
        return {
            "total": total,
            "by_status": by_status,
            "pending": by_status.get("pending", 0),
            "failed": by_status.get("failed", 0),
        }
