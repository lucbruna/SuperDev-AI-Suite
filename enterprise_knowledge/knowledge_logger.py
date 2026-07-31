"""Logging for the Knowledge Graph & Enterprise Memory Engine."""

from __future__ import annotations

import logging

_LOGGER_NAME = "superdev.enterprise_knowledge"


def get_logger(name: str = "") -> logging.Logger:
    full = f"{_LOGGER_NAME}.{name}" if name else _LOGGER_NAME
    return logging.getLogger(full)
