"""Data Platform Logger — Logging for data platform operations."""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class DataLogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DataPlatformLogger:
    def __init__(self):
        self._entries: List[Dict[str, Any]] = []

    def log(self, level: DataLogLevel, message: str, component: str = "", details: Dict[str, Any] = None) -> None:
        self._entries.append({
            "level": level.value,
            "message": message,
            "component": component,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        })

    def debug(self, message: str, component: str = "", details: Dict[str, Any] = None) -> None:
        self.log(DataLogLevel.DEBUG, message, component, details)

    def info(self, message: str, component: str = "", details: Dict[str, Any] = None) -> None:
        self.log(DataLogLevel.INFO, message, component, details)

    def warning(self, message: str, component: str = "", details: Dict[str, Any] = None) -> None:
        self.log(DataLogLevel.WARNING, message, component, details)

    def error(self, message: str, component: str = "", details: Dict[str, Any] = None) -> None:
        self.log(DataLogLevel.ERROR, message, component, details)

    def critical(self, message: str, component: str = "", details: Dict[str, Any] = None) -> None:
        self.log(DataLogLevel.CRITICAL, message, component, details)

    def get_entries(self, level: Optional[DataLogLevel] = None) -> List[Dict[str, Any]]:
        if level:
            return [e for e in self._entries if e["level"] == level.value]
        return list(self._entries)

    def get_entries_by_component(self, component: str) -> List[Dict[str, Any]]:
        return [e for e in self._entries if e["component"] == component]

    def clear(self) -> None:
        self._entries.clear()

    @property
    def count(self) -> int:
        return len(self._entries)
