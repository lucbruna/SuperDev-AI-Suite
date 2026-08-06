"""Small environment helpers shared by the Digital Twin configs.

Every variable uses the module prefix ``SUPERDEV_DT_*`` (plus an optional
area prefix such as ``SYNC_`` for area-specific configs).
"""
from __future__ import annotations

import os

from modules.digital_twin.config.constants import ENV_PREFIX


def env_str(key: str, default: str) -> str:
    raw = os.getenv(ENV_PREFIX + key)
    if raw is None:
        return default
    return raw.strip()


def env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(ENV_PREFIX + key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_int(key: str, default: int) -> int:
    raw = os.getenv(ENV_PREFIX + key)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def env_float(key: str, default: float) -> float:
    raw = os.getenv(ENV_PREFIX + key)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw.strip())
    except ValueError:
        return default
