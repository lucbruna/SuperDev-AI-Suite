"""Planner configuration — task decomposition and planning behaviour.

Environment prefix: ``SUPERDEV_AD_PLANNER_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


@dataclass(slots=True)
class PlannerConfig:
    """Configuration for the project and task planners."""

    decompose_tasks: bool = True
    max_tasks_per_request: int = 20
    max_depth: int = 5
    topo_sort: bool = True
    parallel_planning: bool = False
    default_priority: str = "medium"  # low | medium | high | critical
    require_impact_analysis: bool = True
    estimate_from_history: bool = True
    max_estimation_hours: float = 40.0

    @classmethod
    def from_env(cls) -> PlannerConfig:
        cfg = cls()
        cfg.decompose_tasks = _env_bool("SUPERDEV_AD_PLANNER_DECOMPOSE", cfg.decompose_tasks)
        cfg.max_tasks_per_request = _env_int(
            "SUPERDEV_AD_PLANNER_MAX_TASKS", cfg.max_tasks_per_request
        )
        cfg.topo_sort = _env_bool("SUPERDEV_AD_PLANNER_TOPO_SORT", cfg.topo_sort)
        cfg.require_impact_analysis = _env_bool(
            "SUPERDEV_AD_PLANNER_IMPACT", cfg.require_impact_analysis
        )
        cfg.default_priority = os.getenv(
            "SUPERDEV_AD_PLANNER_PRIORITY", cfg.default_priority
        )
        return cfg
