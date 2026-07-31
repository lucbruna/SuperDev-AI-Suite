"""Logging helpers for the automation engine."""

from __future__ import annotations

import logging

_LOGGER_NAME = "superdev.automation"


def get_logger(name: str = "") -> logging.Logger:
    if name:
        return logging.getLogger(f"{_LOGGER_NAME}.{name}")
    return logging.getLogger(_LOGGER_NAME)


def configure(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s — %(message)s"))
    root = logging.getLogger(_LOGGER_NAME)
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)
