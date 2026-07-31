"""Knowledge Engine Logger — Logging for knowledge operations."""

from datetime import datetime
from enum import Enum
from typing import Any


class KnowledgeLogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class KnowledgeLogger:
    def __init__(self):
        self._entries: list[dict[str, Any]] = []

    def log(self, level: KnowledgeLogLevel, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self._entries.append(
            {
                "level": level.value,
                "message": message,
                "component": component,
                "timestamp": datetime.now().isoformat(),
                "details": details or {},
            }
        )

    def debug(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(KnowledgeLogLevel.DEBUG, message, component, details)

    def info(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(KnowledgeLogLevel.INFO, message, component, details)

    def warning(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(KnowledgeLogLevel.WARNING, message, component, details)

    def error(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(KnowledgeLogLevel.ERROR, message, component, details)

    def critical(self, message: str, component: str = "", details: dict[str, Any] = None) -> None:
        self.log(KnowledgeLogLevel.CRITICAL, message, component, details)

    def get_entries(self, level: KnowledgeLogLevel | None = None) -> list[dict[str, Any]]:
        if level:
            return [e for e in self._entries if e["level"] == level.value]
        return list(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    @property
    def count(self) -> int:
        return len(self._entries)
