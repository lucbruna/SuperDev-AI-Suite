"""Cybersecurity Engine Logger — Logging for security operations."""
from datetime import datetime
from enum import Enum
from typing import Any


class SecurityLogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class SecurityLogger:
    def __init__(self):
        self._entries: list[dict[str, Any]] = []

    def log(self, level: SecurityLogLevel, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self._entries.append({
            "level": level.value,
            "message": message,
            "component": component,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        })

    def debug(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(SecurityLogLevel.DEBUG, message, component, details)

    def info(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(SecurityLogLevel.INFO, message, component, details)

    def warning(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(SecurityLogLevel.WARNING, message, component, details)

    def error(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(SecurityLogLevel.ERROR, message, component, details)

    def critical(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(SecurityLogLevel.CRITICAL, message, component, details)

    def get_entries(self, level: SecurityLogLevel | None = None) -> list[dict[str, Any]]:
        if level:
            return [e for e in self._entries if e["level"] == level.value]
        return list(self._entries)

    def get_entries_by_component(self, component: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if e["component"] == component]

    def clear(self) -> None:
        self._entries.clear()

    @property
    def count(self) -> int:
        return len(self._entries)
