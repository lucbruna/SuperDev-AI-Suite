"""Monitoring configuration for the Digital Twin module.

Environment prefix: ``SUPERDEV_DT_MON_*``.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.config._env import env_bool, env_float, env_int


@dataclass(slots=True)
class MonitoringConfig:
    """Configuration for health checks and anomaly detection."""

    enabled: bool = True
    interval_seconds: int = 15
    alert_threshold: float = 0.8
    anomaly_window: int = 10

    @classmethod
    def from_env(cls) -> "MonitoringConfig":
        cfg = cls()
        cfg.enabled = env_bool("MON_ENABLED", cfg.enabled)
        cfg.interval_seconds = env_int("MON_INTERVAL_SECONDS", cfg.interval_seconds)
        cfg.alert_threshold = env_float("MON_ALERT_THRESHOLD", cfg.alert_threshold)
        cfg.anomaly_window = env_int("MON_ANOMALY_WINDOW", cfg.anomaly_window)
        return cfg
