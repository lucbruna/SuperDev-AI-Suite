"""CX Logger — Structured logging for CX operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CXLogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CXLogEntry:
    level: CXLogLevel
    message: str
    source: str = ""
    project_id: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class CXLogger:
    def __init__(self):
        self.entries: list[CXLogEntry] = []

    def log(
        self,
        level: CXLogLevel,
        message: str,
        source: str = "",
        project_id: str = "",
        data: dict[str, Any] | None = None,
    ) -> CXLogEntry:
        entry = CXLogEntry(level=level, message=message, source=source, project_id=project_id, data=data or {})
        self.entries.append(entry)
        return entry

    def debug(self, message: str, **kwargs) -> CXLogEntry:
        return self.log(CXLogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> CXLogEntry:
        return self.log(CXLogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> CXLogEntry:
        return self.log(CXLogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> CXLogEntry:
        return self.log(CXLogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> CXLogEntry:
        return self.log(CXLogLevel.CRITICAL, message, **kwargs)

    def get_entries(self, level: CXLogLevel | None = None, source: str = "", limit: int = 100) -> list[CXLogEntry]:
        entries = self.entries
        if level:
            entries = [e for e in entries if e.level == level]
        if source:
            entries = [e for e in entries if e.source == source]
        return entries[-limit:]

    def count(self) -> int:
        return len(self.entries)
