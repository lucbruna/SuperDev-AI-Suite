"""Mobile Logger - Structured logging for mobile/edge platform."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    level: LogLevel
    message: str
    source: str = ""
    device_id: str = ""
    module: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class MobileLogger:
    def __init__(self):
        self.entries: list[LogEntry] = []
        self.min_level: LogLevel = LogLevel.DEBUG
        self.filters: dict[str, Any] = {}

    def log(
        self,
        level: LogLevel,
        message: str,
        source: str = "",
        device_id: str = "",
        module: str = "",
        data: dict[str, Any] = None,
    ) -> LogEntry:
        entry = LogEntry(
            level=level, message=message, source=source, device_id=device_id, module=module, data=data or {}
        )
        self.entries.append(entry)
        return entry

    def debug(self, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.CRITICAL, message, **kwargs)

    def get_entries(
        self, level: LogLevel = None, device_id: str = "", module: str = "", limit: int = 100
    ) -> list[LogEntry]:
        entries = self.entries
        if level:
            entries = [e for e in entries if e.level == level]
        if device_id:
            entries = [e for e in entries if e.device_id == device_id]
        if module:
            entries = [e for e in entries if e.module == module]
        return entries[-limit:]

    def count(self, level: LogLevel = None) -> int:
        if level:
            return sum(1 for e in self.entries if e.level == level)
        return len(self.entries)

    def clear(self) -> int:
        count = len(self.entries)
        self.entries.clear()
        return count
