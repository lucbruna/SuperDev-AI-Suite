"""Avatar logger — structured, rate-limited logging for the avatar pillar."""
from __future__ import annotations

import logging
import time
from typing import Any

_LOGGER = logging.getLogger("ai_video_studio.avatar")


class AvatarLogger:
    """Small structured logger with a compact recent-events ring buffer."""

    def __init__(self, capacity: int = 200) -> None:
        self.capacity = max(10, capacity)
        self._events: list[dict[str, Any]] = []

    def _emit(self, level: int, event: str, **context: Any) -> None:
        record: dict[str, Any] = {
            "ts": round(time.time(), 3),
            "event": event,
            "level": logging.getLevelName(level),
            **context,
        }
        self._events.append(record)
        if len(self._events) > self.capacity:
            self._events.pop(0)
        _LOGGER.log(level, "%s %s", event, context)

    def info(self, event: str, **context: Any) -> None:
        self._emit(logging.INFO, event, **context)

    def warn(self, event: str, **context: Any) -> None:
        self._emit(logging.WARNING, event, **context)

    def error(self, event: str, **context: Any) -> None:
        self._emit(logging.ERROR, event, **context)

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return list(self._events[-limit:])


_avatar_logger: AvatarLogger | None = None


def get_avatar_logger() -> AvatarLogger:
    global _avatar_logger
    if _avatar_logger is None:
        _avatar_logger = AvatarLogger()
    return _avatar_logger
