"""Retention policies for knowledge records."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import AccessLevel, MemoryRecord


class RetentionPolicy:
    """Applies retention (days) and purges expired records."""

    def __init__(self, default_days: int = 365) -> None:
        self.default_days = max(1, default_days)
        self._overrides: dict[AccessLevel, int] = {}

    def set_override(self, level: AccessLevel, days: int) -> None:
        self._overrides[level] = max(1, int(days))

    def days_for(self, level: AccessLevel = AccessLevel.INTERNAL) -> int:
        return self._overrides.get(level, self.default_days)

    def is_expired(self, record: MemoryRecord,
                   now: float | None = None) -> bool:
        now = now if now is not None else time.time()
        days = self.days_for()
        return (now - record.created_at) > days * 86400.0

    def purge(self, records: list[MemoryRecord],
              now: float | None = None) -> list[MemoryRecord]:
        now = now if now is not None else time.time()
        return [record for record in records
                if not self.is_expired(record, now)]
