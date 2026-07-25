import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Optional


class StructuredLogger:
    def __init__(self, name: str, level: int = logging.INFO) -> None:
        self._name = name
        self._level = level
        self._handlers: list[logging.Handler] = []

    def set_level(self, level: int) -> None:
        self._level = level

    def add_handler(self, handler: logging.Handler) -> None:
        self._handlers.append(handler)

    def _log(self, level_name: str, level_int: int, msg: str, **context: Any) -> None:
        if level_int < self._level:
            return
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level_name,
            "logger": self._name,
            "message": msg,
            "context": context,
        }
        exc = context.pop("exc_info", None)
        if exc and isinstance(exc, BaseException):
            record["traceback"] = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )
        line = json.dumps(record, default=str)
        for handler in self._handlers:
            handler.emit(
                logging.LogRecord(
                    self._name,
                    level_int,
                    pathname="",
                    lineno=0,
                    msg=line,
                    args=(),
                    exc_info=None,
                )
            )
        print(line)

    def info(self, msg: str, **context: Any) -> None:
        self._log("INFO", logging.INFO, msg, **context)

    def warn(self, msg: str, **context: Any) -> None:
        self._log("WARN", logging.WARN, msg, **context)

    def error(self, msg: str, **context: Any) -> None:
        self._log("ERROR", logging.ERROR, msg, **context)

    def debug(self, msg: str, **context: Any) -> None:
        self._log("DEBUG", logging.DEBUG, msg, **context)
