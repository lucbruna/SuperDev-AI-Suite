"""Image logger — structured logging for the image generator subsystem."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("ai_video_studio.image_generator")


class ImageLogger:
    """Wraps the standard logger for image generation events."""

    def info(self, message: str, **extra: Any) -> None:
        logger.info(message, extra={"image_generator": True, **extra})

    def warning(self, message: str, **extra: Any) -> None:
        logger.warning(message, extra={"image_generator": True, **extra})

    def error(self, message: str, **extra: Any) -> None:
        logger.error(message, extra={"image_generator": True, **extra})

    def generation(self, prompt: str, style: str, ok: bool, **extra: Any) -> None:
        level = logger.info if ok else logger.error
        level(
            "image generation finished",
            extra={"image_generator": True, "prompt": prompt[:80], "style": style, "ok": ok, **extra},
        )


_image_logger: ImageLogger | None = None


def get_image_logger() -> ImageLogger:
    global _image_logger
    if _image_logger is None:
        _image_logger = ImageLogger()
    return _image_logger
