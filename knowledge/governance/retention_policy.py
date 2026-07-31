from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any


class RetentionPolicy:
    """Determines whether records have expired based on retention days."""

    def __init__(self, retention_days: int = 365) -> None:
        self._log = logging.getLogger("superdev.knowledge.governance.retention_policy")
        self.retention_days = max(1, retention_days)

    def is_expired(self, created_at: str) -> bool:
        try:
            created = datetime.fromisoformat(created_at)
        except (TypeError, ValueError):
            return False
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        return created < cutoff

    def filter_expired(self, records: list[Any]) -> list[Any]:
        expired = []
        for record in records:
            created_at = getattr(record, "created_at", "")
            if created_at and self.is_expired(created_at):
                expired.append(record)
        return expired
