"""Environment helpers for the Self-Healing Engine configs."""
from __future__ import annotations

import os

from modules.self_healing_engine.config.constants import ENV_PREFIX

_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def _full(name: str, prefix: str = ENV_PREFIX) -> str:
    return f"{prefix}{name}"


def env_str(name: str, default: str, prefix: str = ENV_PREFIX) -> str:
    value = os.environ.get(_full(name, prefix))
    return value if value is not None else default


def env_bool(name: str, default: bool, prefix: str = ENV_PREFIX) -> bool:
    value = os.environ.get(_full(name, prefix))
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    # Unknown values are treated as False (same semantics as the AD module).
    return False


def env_int(name: str, default: int, prefix: str = ENV_PREFIX) -> int:
    value = os.environ.get(_full(name, prefix))
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def env_float(name: str, default: float, prefix: str = ENV_PREFIX) -> float:
    value = os.environ.get(_full(name, prefix))
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default
