"""Logging helper for the Data Intelligence Engine."""

from __future__ import annotations

import logging


def get_logger(name: str = "superdev.data_intelligence") -> logging.Logger:
    return logging.getLogger(name)
