"""Logger Manager — centralized logging for the SuperDev platform.

Wraps the existing backend/log_config.py and backend/audit/audit_logger.py
into a unified logging service controlled by the orchestrator.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .types import ServiceStatus, now_iso


class LoggingConfig(BaseModel):
    level: str = Field(default="INFO")
    format: str = Field(default="json")  # "json" or "text"
    output: str = Field(default="stdout")  # "stdout", "file", or "both"
    file_path: str = Field(default="logs/superdev.log")
    max_file_size_mb: int = Field(default=100, ge=1)
    backup_count: int = Field(default=5, ge=0)
    include_trace_id: bool = Field(default=True)
    capture_warnings: bool = Field(default=True)
    audit_enabled: bool = Field(default=True)


class JsonFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        for attr in ("trace_id", "service", "user_id", "correlation_id"):
            value = getattr(record, attr, None)
            if value:
                log_entry[attr] = value
        return json.dumps(log_entry, ensure_ascii=False)


class LoggerManager:
    """Unified logging service controlled by the orchestrator.

    Provides:
    - Structured JSON logging (stdout + file)
    - Audit trail for sensitive operations
    - Per-service loggers with consistent formatting
    - Trace ID propagation for request tracking
    - Log level management at runtime
    """

    def __init__(self) -> None:
        self._config: LoggingConfig | None = None
        self._root_logger: logging.Logger | None = None
        self._service_loggers: dict[str, logging.Logger] = {}
        self._audit_log: list[dict[str, Any]] = []
        self._initialized = False

    async def initialize(self, config: LoggingConfig | None = None) -> None:
        """Initialize the logging system with the given configuration."""
        self._config = config or LoggingConfig()

        root = logging.getLogger("superdev")
        root.setLevel(getattr(logging, self._config.level, logging.INFO))
        root.handlers.clear()

        # Console handler
        if self._config.output in ("stdout", "both"):
            console = logging.StreamHandler(sys.stdout)
            if self._config.format == "json":
                console.setFormatter(JsonFormatter())
            else:
                console.setFormatter(logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                ))
            root.addHandler(console)

        # File handler with rotation
        if self._config.output in ("file", "both") and self._config.file_path:
            log_path = Path(self._config.file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                from logging.handlers import RotatingFileHandler
                fh = RotatingFileHandler(
                    filename=str(log_path),
                    maxBytes=self._config.max_file_size_mb * 1024 * 1024,
                    backupCount=self._config.backup_count,
                    encoding="utf-8",
                )
                fh.setFormatter(JsonFormatter())
                root.addHandler(fh)
            except Exception:
                pass  # Fall back to console-only

        # Capture Python warnings
        if self._config.capture_warnings:
            logging.captureWarnings(True)

        self._root_logger = root
        self._initialized = True

    # ─── Logger Access ────────────────────────────────────────────────────

    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a named logger."""
        if name in self._service_loggers:
            return self._service_loggers[name]

        logger = logging.getLogger(f"superdev.{name}")
        self._service_loggers[name] = logger
        return logger

    def get_service_logger(self, service_name: str) -> logging.Logger:
        """Get a logger specifically for a platform service."""
        return self.get_logger(f"svc.{service_name}")

    # ─── Logging Methods ──────────────────────────────────────────────────

    def debug(self, message: str, **kwargs: Any) -> None:
        if self._root_logger:
            self._root_logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        if self._root_logger:
            self._root_logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        if self._root_logger:
            self._root_logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        if self._root_logger:
            self._root_logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        if self._root_logger:
            self._root_logger.critical(message, extra=kwargs)

    # ─── Audit Trail ──────────────────────────────────────────────────────

    async def audit(
        self,
        action: str,
        user_id: str = "",
        resource: str = "",
        details: dict[str, Any] | None = None,
        success: bool = True,
    ) -> None:
        """Record an audit event for compliance tracking."""
        entry = {
            "timestamp": now_iso(),
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "details": details or {},
            "success": success,
        }
        self._audit_log.append(entry)
        if len(self._audit_log) > 10_000:
            self._audit_log = self._audit_log[-5_000:]

        # Also log as structured log
        if self._root_logger:
            self._root_logger.info(
                f"AUDIT: {action} by {user_id} on {resource}",
                extra={"audit": True, **entry},
            )

    def get_audit_log(
        self, limit: int = 100, action: str = "",
    ) -> list[dict[str, Any]]:
        """Get recent audit log entries."""
        entries = self._audit_log
        if action:
            entries = [e for e in entries if e["action"] == action]
        return entries[-limit:]

    # ─── Lifecycle ────────────────────────────────────────────────────────

    async def set_level(self, level: str) -> None:
        """Change log level at runtime."""
        level_upper = level.upper()
        if level_upper in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            if self._root_logger:
                self._root_logger.setLevel(getattr(logging, level_upper))
            self.info(f"Log level changed to {level_upper}")

    async def flush(self) -> None:
        """Flush all log handlers."""
        if self._root_logger:
            for handler in self._root_logger.handlers:
                handler.flush()

    async def shutdown(self) -> None:
        """Shutdown the logging system."""
        await self.flush()
        if self._root_logger:
            for handler in list(self._root_logger.handlers):
                handler.close()
                self._root_logger.removeHandler(handler)
        self._initialized = False

    # ─── Status ───────────────────────────────────────────────────────────

    def get_statistics(self) -> dict[str, Any]:
        """Get logging statistics."""
        return {
            "initialized": self._initialized,
            "level": self._config.level if self._config else "N/A",
            "format": self._config.format if self._config else "N/A",
            "output": self._config.output if self._config else "N/A",
            "service_loggers": len(self._service_loggers),
            "audit_entries": len(self._audit_log),
            "config": self._config.model_dump() if self._config else {},
        }
