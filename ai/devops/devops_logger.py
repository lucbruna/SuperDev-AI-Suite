"""DevOps logger."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class DevOpsLogger:
    def __init__(self, max_entries: int = 100000) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max = max_entries
    def log(self, level: LogLevel, message: str, source: str = "") -> Dict[str, Any]:
        entry = {"level": level.value, "message": message, "source": source, "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry
    def info(self, message: str, source: str = "") -> Dict[str, Any]:
        return self.log(LogLevel.INFO, message, source)
    def warning(self, message: str, source: str = "") -> Dict[str, Any]:
        return self.log(LogLevel.WARNING, message, source)
    def error(self, message: str, source: str = "") -> Dict[str, Any]:
        return self.log(LogLevel.ERROR, message, source)
    def query(self, level: Optional[LogLevel] = None, limit: int = 100) -> List[Dict[str, Any]]:
        entries = self._entries
        if level:
            entries = [e for e in entries if e["level"] == level.value]
        return entries[-limit:]
    def count(self) -> int:
        return len(self._entries)
