"""Simulation configuration for the Digital Twin module.

Environment prefix: ``SUPERDEV_DT_SIM_*``.
"""
from __future__ import annotations

from dataclasses import dataclass

from modules.digital_twin.config._env import env_bool, env_float, env_int


@dataclass(slots=True)
class SimulationConfig:
    """Configuration for deterministic what-if scenario simulation."""

    enabled: bool = True
    max_scenarios: int = 20
    default_steps: int = 10
    seed: int = 42
    risk_threshold: float = 0.7
    timeout_seconds: int = 120

    @classmethod
    def from_env(cls) -> "SimulationConfig":
        cfg = cls()
        cfg.enabled = env_bool("SIM_ENABLED", cfg.enabled)
        cfg.max_scenarios = env_int("SIM_MAX_SCENARIOS", cfg.max_scenarios)
        cfg.default_steps = env_int("SIM_DEFAULT_STEPS", cfg.default_steps)
        cfg.seed = env_int("SIM_SEED", cfg.seed)
        cfg.risk_threshold = env_float("SIM_RISK_THRESHOLD", cfg.risk_threshold)
        cfg.timeout_seconds = env_int("SIM_TIMEOUT_SECONDS", cfg.timeout_seconds)
        return cfg
