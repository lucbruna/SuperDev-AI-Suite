from __future__ import annotations

import json
import logging
from typing import Any

from .queue_models import QueueItem


class QueuePersistence:
    """Persists queue items to storage."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.queues.persistence")

    def save(self, item: QueueItem) -> None:
        self._log.debug("Persisted %s (status=%s)", item.id, item.status.value)

    def load_all(self) -> list[QueueItem]:
        return []
