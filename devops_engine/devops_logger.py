"""Logging for the DevOps & Cloud Infrastructure Engine (Volume 37)."""

from __future__ import annotations

import logging

_NAMESPACE = "superdev.devops_engine"


def get_logger(name: str = "core") -> logging.Logger:
    return logging.getLogger(f"{_NAMESPACE}.{name}")
