from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class MemoryLogEntry:
    """A single log entry for a memory operation."""

    def __init__(
        self,
        level: str,
        message: str,
        operation: str = "",
        key: str = "",
        details: Dict[str, Any] | None = None,
    ):
        self._timestamp = time.time()
        self._level = level
        self._message = message
        self._operation = operation
        self._key = key
        self._details = details or {}

    @property
    def timestamp(self) -> float:
        return self._timestamp

    @property
    def level(self) -> str:
        return self._level

    @property
    def message(self) -> str:
        return self._message

    @property
    def operation(self) -> str:
        return self._operation

    @property
    def key(self) -> str:
        return self._key

    @property
    def details(self) -> Dict[str, Any]:
        return dict(self._details)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self._timestamp,
            "level": self._level,
            "message": self._message,
            "operation": self._operation,
            "key": self._key,
            "details": dict(self._details),
        }


class MemoryLogger:
    """Structured logger for the memory subsystem."""

    def __init__(self, max_entries: int = 10000):
        self._entries: List[MemoryLogEntry] = []
        self._max_entries = max_entries

    def info(self, message: str, operation: str = "", key: str = "", details: Dict[str, Any] | None = None) -> None:
        self._log("INFO", message, operation, key, details)

    def warn(self, message: str, operation: str = "", key: str = "", details: Dict[str, Any] | None = None) -> None:
        self._log("WARN", message, operation, key, details)

    def error(self, message: str, operation: str = "", key: str = "", details: Dict[str, Any] | None = None) -> None:
        self._log("ERROR", message, operation, key, details)

    def debug(self, message: str, operation: str = "", key: str = "", details: Dict[str, Any] | None = None) -> None:
        self._log("DEBUG", message, operation, key, details)

    def _log(self, level: str, message: str, operation: str, key: str, details: Dict[str, Any] | None) -> None:
        entry = MemoryLogEntry(level, message, operation, key, details)
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries.pop(0)

    def get_entries(
        self,
        level: str | None = None,
        operation: str | None = None,
        limit: int = 100,
    ) -> List[MemoryLogEntry]:
        results = list(self._entries)
        if level:
            results = [e for e in results if e.level == level]
        if operation:
            results = [e for e in results if e.operation == operation]
        return results[-limit:]

    def get_errors(self, limit: int = 100) -> List[MemoryLogEntry]:
        return self.get_entries(level="ERROR", limit=limit)

    def clear(self) -> None:
        self._entries.clear()

    @property
    def size(self) -> int:
        return len(self._entries)

    def to_dict_list(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self._entries]
