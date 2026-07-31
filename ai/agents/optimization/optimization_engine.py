"""Optimization engine for performance tuning and resource management."""

from __future__ import annotations

from typing import Any

from .bottleneck_resolver import BottleneckResolver
from .capacity_planner import CapacityPlanner
from .performance_tuner import PerformanceTuner
from .resource_optimizer import ResourceOptimizer


class OptimizationEngine:
    """Central engine for optimizing agent performance and resource usage."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}
        self._resources = ResourceOptimizer()
        self._tuner = PerformanceTuner()
        self._bottlenecks = BottleneckResolver()
        self._capacity = CapacityPlanner()
        self._optimization_count: int = 0

    def optimize(self, context: dict[str, Any]) -> dict[str, Any]:
        self._optimization_count += 1
        resource_opt = self._resources.optimize(context)
        perf_opt = self._tuner.tune(context)
        return {
            "resource_optimization": resource_opt,
            "performance_optimization": perf_opt,
            "total_optimizations": self._optimization_count,
        }

    def identify_bottlenecks(self, metrics: dict[str, Any]) -> list[dict[str, Any]]:
        return self._bottlenecks.identify(metrics)

    def plan_capacity(self, demand: dict[str, Any]) -> dict[str, Any]:
        return self._capacity.plan(demand)

    def get_metrics(self) -> dict[str, Any]:
        return {"total_optimizations": self._optimization_count}
