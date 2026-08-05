"""Voice Logger — centralised structured logging for the AI Voice Studio."""
from __future__ import annotations

import logging

_LOGGER = None


def get_logger() -> logging.Logger:
    global _LOGGER
    if _LOGGER is None:
        _LOGGER = logging.getLogger("ai_voice_studio")
    return _LOGGER


def log_synthesis(voice_id: str, engine: str, duration: float, path: str) -> None:
    get_logger().info(
        "voice synthesis done",
        extra={"voice": voice_id, "engine": engine, "duration": duration, "path": path},
    )
