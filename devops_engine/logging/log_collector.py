"""Log collection (Volume 37, Fase 4)."""

from __future__ import annotations

from devops_engine.devops_models import LogEntry
from devops_engine.devops_protocols import new_id, now


class LogCollector:
    """Collects raw log entries."""

    def __init__(self) -> None:
        self._entries: list[LogEntry] = []

    def collect(self, source: str, message: str, level: str = "info",
                host: str = "") -> LogEntry:
        entry = LogEntry(
            log_id=new_id("log"),
            source=source,
            level=level,
            message=message,
            host=host,
            timestamp=now(),
        )
        self._entries.append(entry)
        return entry

    def entries(self) -> list[LogEntry]:
        return list(self._entries)

    def count(self) -> int:
        return len(self._entries)
