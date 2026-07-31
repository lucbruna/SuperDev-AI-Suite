"""Security logger for audit trails and security events."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class SecurityLogger:
    """Structured logger for all security operations."""

    def __init__(self, log_level: str = "INFO") -> None:
        self._log_level = log_level
        self._entries: List[Dict[str, Any]] = []

    def _log(self, level: str, category: str, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        if self._should_log(level):
            entry = {
                "level": level,
                "category": category,
                "message": message,
                "details": details or {},
                "timestamp": time.time(),
            }
            self._entries.append(entry)

    def _should_log(self, level: str) -> bool:
        levels = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3, "CRITICAL": 4}
        return levels.get(level, 0) >= levels.get(self._log_level, 0)

    def debug(self, category: str, message: str, **kwargs: Any) -> None:
        self._log("DEBUG", category, message, kwargs)

    def info(self, category: str, message: str, **kwargs: Any) -> None:
        self._log("INFO", category, message, kwargs)

    def warn(self, category: str, message: str, **kwargs: Any) -> None:
        self._log("WARN", category, message, kwargs)

    def error(self, category: str, message: str, **kwargs: Any) -> None:
        self._log("ERROR", category, message, kwargs)

    def critical(self, category: str, message: str, **kwargs: Any) -> None:
        self._log("CRITICAL", category, message, kwargs)

    def get_entries(self, level: Optional[str] = None, category: Optional[str] = None,
                    limit: int = 50) -> List[Dict[str, Any]]:
        entries = self._entries
        if level:
            entries = [e for e in entries if e["level"] == level]
        if category:
            entries = [e for e in entries if e["category"] == category]
        return entries[-limit:]

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()
