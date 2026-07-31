"""Logging for the Agent Orchestration Engine (Volume 31)."""

from __future__ import annotations

import logging

_PREFIX = "superdev.agent_orchestration"


def get_logger(name: str = "orchestrator") -> logging.Logger:
    return logging.getLogger(f"{_PREFIX}.{name}")
