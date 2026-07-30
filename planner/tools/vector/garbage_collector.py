from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


class GarbageCollector:
    """Remove stale or orphaned vectors from the store."""

    def __init__(self):
        self._orphans: list[str] = []
        self._stats: dict[str, Any] = {"collected": 0, "expired": 0}

    def collect_orphans(self, known_ids: set[str], stored_ids: set[str]) -> list[str]:
        orphans = stored_ids - known_ids
        self._orphans = list(orphans)
        self._stats["collected"] += len(orphans)
        return self._orphans

    def collect_expired(self, timestamps: dict[str, datetime], ttl: timedelta = timedelta(days=30)) -> list[str]:
        now = datetime.now()
        expired = [doc_id for doc_id, ts in timestamps.items() if now - ts > ttl]
        self._stats["expired"] += len(expired)
        return expired

    def stats(self) -> dict[str, Any]:
        return {**self._stats}
