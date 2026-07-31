"""Digital Twin logger."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

class TwinLogger:
    def __init__(self, max_entries: int = 100000) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._max = max_entries
    def log(self, level: LogLevel, message: str, source: str = "", twin_id: str = "") -> Dict[str, Any]:
        entry = {"level": level.value, "message": message, "source": source, "twin_id": twin_id, "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max:]
        return entry
    def info(self, message: str, source: str = "", twin_id: str = "") -> Dict[str, Any]:
        return self.log(LogLevel.INFO, message, source, twin_id)
    def warning(self, message: str, source: str = "", twin_id: str = "") -> Dict[str, Any]:
        return self.log(LogLevel.WARNING, message, source, twin_id)
    def error(self, message: str, source: str = "", twin_id: str = "") -> Dict[str, Any]:
        return self.log(LogLevel.ERROR, message, source, twin_id)
    def query(self, level: Optional[LogLevel] = None, twin_id: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        entries = self._entries
        if level:
            entries = [e for e in entries if e["level"] == level.value]
        if twin_id:
            entries = [e for e in entries if e.get("twin_id") == twin_id]
        return entries[-limit:]
    def count(self) -> int:
        return len(self._entries)
