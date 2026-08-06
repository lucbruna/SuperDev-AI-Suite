"""Optimization subsystem configuration."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OptimizationConfig:
    """Deterministic optimization behaviour."""

    enabled: bool = True
    max_suggestions_per_cycle: int = 10
    cache_hit_target: float = 0.9
    dependency_duplication_threshold: int = 3
