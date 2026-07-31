"""BI Logger — Structured logging for BI operations."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class BILogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class BILogEntry:
    level: BILogLevel
    message: str
    source: str = ""
    project_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class BILogger:
    def __init__(self):
        self.entries: List[BILogEntry] = []

    def log(self, level: BILogLevel, message: str, source: str = "", project_id: str = "", data: Dict[str, Any] = None) -> BILogEntry:
        entry = BILogEntry(level=level, message=message, source=source, project_id=project_id, data=data or {})
        self.entries.append(entry)
        return entry

    def debug(self, message: str, **kwargs) -> BILogEntry:
        return self.log(BILogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs) -> BILogEntry:
        return self.log(BILogLevel.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs) -> BILogEntry:
        return self.log(BILogLevel.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs) -> BILogEntry:
        return self.log(BILogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs) -> BILogEntry:
        return self.log(BILogLevel.CRITICAL, message, **kwargs)

    def get_entries(self, level: BILogLevel = None, source: str = "", limit: int = 100) -> List[BILogEntry]:
        entries = self.entries
        if level:
            entries = [e for e in entries if e.level == level]
        if source:
            entries = [e for e in entries if e.source == source]
        return entries[-limit:]

    def count(self) -> int:
        return len(self.entries)
