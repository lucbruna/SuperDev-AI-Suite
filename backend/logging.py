from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from backend.settings import LoggingSettings


class LogConfig(BaseModel):
    level: str = Field(default="INFO")
    format: str = Field(default="json")
    output_file: str | None = Field(default=None)
    include_trace_id: bool = Field(default=True)
    console: bool = Field(default=True)
    retention_days: int = Field(default=30)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "trace_id"):
            log_entry["trace_id"] = record.trace_id
        return json.dumps(log_entry)


def setup_logging(settings: LoggingSettings) -> logging.Logger:
    logger = logging.getLogger("superdev")
    logger.setLevel(settings.level.upper())
    logger.handlers.clear()

    if settings.console:
        console_handler = logging.StreamHandler(sys.stdout)
        if settings.format == "json":
            console_handler.setFormatter(JsonFormatter())
        else:
            console_handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
            )
        logger.addHandler(console_handler)

    if settings.output_file:
        log_path = Path(settings.output_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)

    return logger