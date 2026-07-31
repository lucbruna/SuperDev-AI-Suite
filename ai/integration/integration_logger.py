"""
Integration Logger - Structured logging for integrations
"""
import hashlib
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
    entry_id: str
    level: LogLevel
    message: str
    integration_id: str = ""
    source: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    trace_id: str = ""


class IntegrationLogger:
    def __init__(self):
        self.entries: list[LogEntry] = []
        self.min_level: LogLevel = LogLevel.INFO
        self.sinks: list[str] = ["console"]
        self.filters: dict[str, Any] = {}

    def log(self, level: LogLevel, message: str, integration_id: str = "", data: dict[str, Any] = None, **kwargs) -> LogEntry | None:
        if level.value < self.min_level.value:
            return None
        entry = LogEntry(entry_id=hashlib.sha256(f"{message}{datetime.now().isoformat()}".encode()).hexdigest()[:16], level=level, message=message, integration_id=integration_id, data=data or {}, **kwargs)
        self.entries.append(entry)
        return entry

    def debug(self, message: str, integration_id: str = "", **kwargs) -> LogEntry | None:
        return self.log(LogLevel.DEBUG, message, integration_id, **kwargs)

    def info(self, message: str, integration_id: str = "", **kwargs) -> LogEntry | None:
        return self.log(LogLevel.INFO, message, integration_id, **kwargs)

    def warning(self, message: str, integration_id: str = "", **kwargs) -> LogEntry | None:
        return self.log(LogLevel.WARNING, message, integration_id, **kwargs)

    def error(self, message: str, integration_id: str = "", **kwargs) -> LogEntry | None:
        return self.log(LogLevel.ERROR, message, integration_id, **kwargs)

    def critical(self, message: str, integration_id: str = "", **kwargs) -> LogEntry | None:
        return self.log(LogLevel.CRITICAL, message, integration_id, **kwargs)

    def get_entries(self, level: LogLevel = None, integration_id: str = None, limit: int = 100) -> list[LogEntry]:
        results = self.entries
        if level:
            results = [e for e in results if e.level == level]
        if integration_id:
            results = [e for e in results if e.integration_id == integration_id]
        return results[-limit:]

    def set_min_level(self, level: LogLevel) -> None:
        self.min_level = level

    def add_sink(self, sink: str) -> None:
        if sink not in self.sinks:
            self.sinks.append(sink)

    def clear(self) -> None:
        self.entries.clear()

    def count(self) -> int:
        return len(self.entries)
