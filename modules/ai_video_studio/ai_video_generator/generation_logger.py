"""Generation logger — structured logging for the generator subsystem."""
from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger("ai_video_studio.video_generator")


class GenerationLogger:
    """Wraps the standard logger with generation-specific helpers."""

    def __init__(self) -> None:
        self._started = time.time()

    def info(self, message: str, **extra: Any) -> None:
        logger.info(message, extra={"video_generator": True, **extra})

    def warning(self, message: str, **extra: Any) -> None:
        logger.warning(message, extra={"video_generator": True, **extra})

    def error(self, message: str, **extra: Any) -> None:
        logger.error(message, extra={"video_generator": True, **extra})

    def job(self, job_id: str, message: str, **extra: Any) -> None:
        logger.info(
            message,
            extra={"video_generator": True, "job_id": job_id, **extra},
        )


_generation_logger: GenerationLogger | None = None


def get_generation_logger() -> GenerationLogger:
    global _generation_logger
    if _generation_logger is None:
        _generation_logger = GenerationLogger()
    return _generation_logger
