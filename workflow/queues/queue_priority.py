from __future__ import annotations

from typing import Any

from .queue_models import QueueItem, QueueStatus


class QueuePriority:
    """Resolves highest-priority item from the queue."""

    @staticmethod
    def highest(items: list[QueueItem]) -> QueueItem | None:
        pending = [i for i in items if i.status == QueueStatus.PENDING]
        if not pending:
            return None
        return max(pending, key=lambda i: (i.priority, -i.created_at))
