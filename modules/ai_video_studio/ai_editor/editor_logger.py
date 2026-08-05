"""Editor logger — module loggers plus an in-memory ring buffer.

The ring buffer keeps the last ``N`` formatted log lines so a UI can show an
"editor console" without tailing files. Wraps the shared ``make_logger``.
"""
from __future__ import annotations

import logging
from collections import deque
from typing import Any

from modules.ai_video_studio.editor_common import make_logger

_ring: deque[str] = deque(maxlen=200)


class _RingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        _ring.append(f"{record.asctime} {record.levelname} {record.name}: {record.getMessage()}")


def get_editor_logger(name: str = "editor") -> logging.Logger:
    """Logger with the ring handler attached exactly once."""
    logger = make_logger(name)
    if not any(isinstance(h, _RingHandler) for h in logger.handlers):
        handler = _RingHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s", datefmt="%H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def recent_logs(limit: int = 50) -> list[str]:
    """Last ``limit`` log lines (newest last)."""
    return list(_ring)[-limit:]


def clear_logs() -> None:
    _ring.clear()
