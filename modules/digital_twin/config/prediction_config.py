"""Prediction configuration for the Digital Twin module.

Environment prefix: ``SUPERDEV_DT_PRED_*``.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.config._env import env_bool, env_float, env_int, env_str


@dataclass(slots=True)
class PredictionConfig:
    """Configuration for trend and impact prediction."""

    enabled: bool = True
    horizon_steps: int = 5
    min_history: int = 3
    confidence_threshold: float = 0.6
    method: str = "linear"

    @classmethod
    def from_env(cls) -> "PredictionConfig":
        cfg = cls()
        cfg.enabled = env_bool("PRED_ENABLED", cfg.enabled)
        cfg.horizon_steps = env_int("PRED_HORIZON_STEPS", cfg.horizon_steps)
        cfg.min_history = env_int("PRED_MIN_HISTORY", cfg.min_history)
        cfg.confidence_threshold = env_float(
            "PRED_CONFIDENCE_THRESHOLD", cfg.confidence_threshold
        )
        cfg.method = env_str("PRED_METHOD", cfg.method)
        return cfg
