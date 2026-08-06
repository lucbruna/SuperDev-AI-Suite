"""Automation configuration: scheduled maintenance and continuous validation."""
from __future__ import annotations

from dataclasses import dataclass

from modules.self_healing_engine.config._env import (
    env_bool,
    env_int,
    env_str,
)


@dataclass(slots=True)
class AutomationConfig:
    """Policy governing automated maintenance and validation tasks."""

    maintenance_enabled: bool = True
    maintenance_interval_hours: int = 24
    cleanup_interval_hours: int = 12
    optimization_interval_hours: int = 48
    continuous_validation_enabled: bool = True
    validation_interval_seconds: int = 60
    maintenance_window_start: str = "02:00"
    maintenance_window_end: str = "04:00"

    @classmethod
    def from_env(cls) -> "AutomationConfig":
        return cls(
            maintenance_enabled=env_bool("MAINTENANCE_ENABLED", True),
            maintenance_interval_hours=env_int("MAINTENANCE_INTERVAL_HOURS", 24),
            cleanup_interval_hours=env_int("CLEANUP_INTERVAL_HOURS", 12),
            optimization_interval_hours=env_int("OPTIMIZATION_INTERVAL_HOURS", 48),
            continuous_validation_enabled=env_bool(
                "CONTINUOUS_VALIDATION_ENABLED", True
            ),
            validation_interval_seconds=env_int("VALIDATION_INTERVAL_SECONDS", 60),
            maintenance_window_start=env_str("MAINTENANCE_WINDOW_START", "02:00"),
            maintenance_window_end=env_str("MAINTENANCE_WINDOW_END", "04:00"),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "maintenance_enabled": self.maintenance_enabled,
            "maintenance_interval_hours": self.maintenance_interval_hours,
            "cleanup_interval_hours": self.cleanup_interval_hours,
            "optimization_interval_hours": self.optimization_interval_hours,
            "continuous_validation_enabled": self.continuous_validation_enabled,
            "validation_interval_seconds": self.validation_interval_seconds,
            "maintenance_window_start": self.maintenance_window_start,
            "maintenance_window_end": self.maintenance_window_end,
        }
