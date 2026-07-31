"""Logging for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import logging

_PREFIX = "superdev.finance_intelligence"


def get_logger(name: str = "finance") -> logging.Logger:
    return logging.getLogger(f"{_PREFIX}.{name}")
