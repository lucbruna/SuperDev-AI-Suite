"""Log archival."""

from __future__ import annotations

import time
from typing import Any


class LogArchive:
    def __init__(self, retention_days: int = 30) -> None:
        self._retention_days = retention_days
        self._archived: list[dict[str, Any]] = []
        self._total_archived = 0

    def archive(self, entries: list[dict[str, Any]], reason: str = "retention") -> dict[str, Any]:
        archive_entry = {
            "archive_id": f"arch_{len(self._archived) + 1}",
            "count": len(entries),
            "reason": reason,
            "timestamp": time.time(),
            "size_estimate": len(entries) * 200,
        }
        self._archived.append(archive_entry)
        self._total_archived += len(entries)
        return archive_entry

    def get_archived(self) -> list[dict[str, Any]]:
        return list(self._archived)

    def total_archived(self) -> int:
        return self._total_archived

    def cleanup(self, max_archives: int = 50) -> int:
        if len(self._archived) > max_archives:
            removed = self._archived[:-max_archives]
            self._archived = self._archived[-max_archives:]
            return len(removed)
        return 0
