from __future__ import annotations

import logging
from typing import Any


class APILogger:
    """Structured logger for the API layer."""

    def __init__(self, name: str = "api", level: str = "INFO") -> None:
        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    def _log(self, level: int, msg: str, **kwargs: Any) -> None:
        if kwargs:
            self._logger.log(level, "%s - %s", msg, kwargs)
        else:
            self._logger.log(level, "%s", msg)

    def info(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, **kwargs)

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, **kwargs)

    def critical(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.CRITICAL, msg, **kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self._logger.name, "level": logging.getLevelName(self._logger.level)}
