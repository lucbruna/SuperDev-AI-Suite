"""ERP Logger — Structured logging for ERP operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ERPLogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ERPLogEntry:
    level: ERPLogLevel
    message: str
    source: str = ""
    project_id: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class ERPLogger:
    def __init__(self):
        self.entries: list[ERPLogEntry] = []

    def log(
        self,
        level: ERPLogLevel,
        message: str,
        source: str = "",
        project_id: str = "",
        data: dict[str, Any] | None = None,
    ) -> ERPLogEntry:
        entry = ERPLogEntry(level=level, message=message, source=source, project_id=project_id, data=data or {})
        self.entries.append(entry)
        return entry

    def debug(self, message: str, **kwargs) -> ERPLogEntry:
        return self.log(ERPLogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> ERPLogEntry:
        return self.log(ERPLogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> ERPLogEntry:
        return self.log(ERPLogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> ERPLogEntry:
        return self.log(ERPLogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> ERPLogEntry:
        return self.log(ERPLogLevel.CRITICAL, message, **kwargs)

    def get_entries(self, level: ERPLogLevel | None = None, source: str = "", limit: int = 100) -> list[ERPLogEntry]:
        entries = self.entries
        if level:
            entries = [e for e in entries if e.level == level]
        if source:
            entries = [e for e in entries if e.source == source]
        return entries[-limit:]

    def count(self) -> int:
        return len(self.entries)
