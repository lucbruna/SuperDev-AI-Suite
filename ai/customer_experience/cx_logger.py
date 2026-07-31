"""CX Logger — Structured logging for CX operations."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


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
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class CXLogger:
    def __init__(self):
        self.entries: List[CXLogEntry] = []

    def log(self, level: CXLogLevel, message: str, source: str = "", project_id: str = "", data: Optional[Dict[str, Any]] = None) -> CXLogEntry:
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

    def get_entries(self, level: Optional[CXLogLevel] = None, source: str = "", limit: int = 100) -> List[CXLogEntry]:
        entries = self.entries
        if level:
            entries = [e for e in entries if e.level == level]
        if source:
            entries = [e for e in entries if e.source == source]
        return entries[-limit:]

    def count(self) -> int:
        return len(self.entries)
