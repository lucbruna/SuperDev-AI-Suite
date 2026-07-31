from __future__ import annotations

import logging


class DevOpsLogger:
    """Logger for DevOps operations with structured output."""

    def __init__(self, name: str = "superdev.devops") -> None:
        self._log = logging.getLogger(name)

    def info(self, message: str, **extra: str) -> None:
        self._log.info(message, extra=extra)

    def warn(self, message: str, **extra: str) -> None:
        self._log.warning(message, extra=extra)

    def error(self, message: str, **extra: str) -> None:
        self._log.error(message, extra=extra)

    def debug(self, message: str, **extra: str) -> None:
        self._log.debug(message, extra=extra)
