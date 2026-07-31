"""Logging helper for the Collaboration & Team Workspace Engine."""

from __future__ import annotations

import logging


def get_logger(name: str = "superdev.collaboration") -> logging.Logger:
    return logging.getLogger(name)
