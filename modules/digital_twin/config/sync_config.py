"""Synchronization configuration for the Digital Twin module.

Environment prefix: ``SUPERDEV_DT_SYNC_*``.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.config._env import env_bool, env_int


@dataclass(slots=True)
class SyncConfig:
    """Configuration for twin <-> reality synchronization."""

    enabled: bool = True
    interval_seconds: int = 30
    full_sync_every: int = 10
    retry_attempts: int = 3
    timeout_seconds: int = 60

    @classmethod
    def from_env(cls) -> "SyncConfig":
        cfg = cls()
        cfg.enabled = env_bool("SYNC_ENABLED", cfg.enabled)
        cfg.interval_seconds = env_int("SYNC_INTERVAL_SECONDS", cfg.interval_seconds)
        cfg.full_sync_every = env_int("SYNC_FULL_EVERY", cfg.full_sync_every)
        cfg.retry_attempts = env_int("SYNC_RETRY_ATTEMPTS", cfg.retry_attempts)
        cfg.timeout_seconds = env_int("SYNC_TIMEOUT_SECONDS", cfg.timeout_seconds)
        return cfg
