from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    AUDIT = "audit"


@dataclass
class LogEntry:
    id: str
    level: LogLevel
    module: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None


class KnowledgeLogger:
    def __init__(self, max_entries: int = 10000, rotation_size: int = 5000):
        self._entries: List[LogEntry] = []
        self._max_entries = max_entries
        self._rotation_size = rotation_size
        self._logger = logging.getLogger("knowledge_engine")

    def log(self, level: LogLevel, module: str, message: str,
            details: Optional[Dict[str, Any]] = None,
            correlation_id: Optional[str] = None,
            user_id: Optional[str] = None) -> LogEntry:
        entry = LogEntry(
            id=str(uuid.uuid4()),
            level=level,
            module=module,
            message=message,
            details=details or {},
            correlation_id=correlation_id,
            user_id=user_id,
        )
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._rotation_size:]
        self._emit(entry)
        return entry

    def debug(self, module: str, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.DEBUG, module, message, **kwargs)

    def info(self, module: str, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.INFO, module, message, **kwargs)

    def warning(self, module: str, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.WARNING, module, message, **kwargs)

    def error(self, module: str, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.ERROR, module, message, **kwargs)

    def critical(self, module: str, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.CRITICAL, module, message, **kwargs)

    def audit(self, module: str, message: str, **kwargs) -> LogEntry:
        return self.log(LogLevel.AUDIT, module, message, **kwargs)

    def log_query(self, query: str, results_count: int, duration_ms: float,
                  correlation_id: Optional[str] = None) -> LogEntry:
        return self.log(LogLevel.INFO, "query", f"Query executed: {query[:100]}",
                        details={"query": query, "results": results_count, "duration_ms": duration_ms},
                        correlation_id=correlation_id)

    def log_performance(self, operation: str, duration_ms: float,
                        correlation_id: Optional[str] = None) -> LogEntry:
        return self.log(LogLevel.DEBUG, "performance", f"{operation} took {duration_ms}ms",
                        details={"operation": operation, "duration_ms": duration_ms},
                        correlation_id=correlation_id)

    def get_logs(self, level: Optional[LogLevel] = None, module: Optional[str] = None,
                 limit: int = 100) -> List[LogEntry]:
        results = self._entries
        if level:
            results = [e for e in results if e.level == level]
        if module:
            results = [e for e in results if e.module == module]
        return results[-limit:]

    def get_errors(self, limit: int = 50) -> List[LogEntry]:
        return [e for e in self._entries if e.level in (LogLevel.ERROR, LogLevel.CRITICAL)][-limit:]

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> None:
        self._entries.clear()

    def _emit(self, entry: LogEntry) -> None:
        msg = f"[{entry.level.value.upper()}] [{entry.module}] {entry.message}"
        if entry.level == LogLevel.DEBUG:
            self._logger.debug(msg)
        elif entry.level == LogLevel.INFO:
            self._logger.info(msg)
        elif entry.level == LogLevel.WARNING:
            self._logger.warning(msg)
        elif entry.level == LogLevel.ERROR:
            self._logger.error(msg)
        elif entry.level in (LogLevel.CRITICAL, LogLevel.AUDIT):
            self._logger.critical(msg)