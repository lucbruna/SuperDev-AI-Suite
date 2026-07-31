"""Optimization engine for performance tuning and resource management."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .resource_optimizer import ResourceOptimizer
from .performance_tuner import PerformanceTuner
from .bottleneck_resolver import BottleneckResolver
from .capacity_planner import CapacityPlanner


class OptimizationEngine:
    """Central engine for optimizing agent performance and resource usage."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._resources = ResourceOptimizer()
        self._tuner = PerformanceTuner()
        self._bottlenecks = BottleneckResolver()
        self._capacity = CapacityPlanner()
        self._optimization_count: int = 0

    def optimize(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._optimization_count += 1
        resource_opt = self._resources.optimize(context)
        perf_opt = self._tuner.tune(context)
        return {
            "resource_optimization": resource_opt,
            "performance_optimization": perf_opt,
            "total_optimizations": self._optimization_count,
        }

    def identify_bottlenecks(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._bottlenecks.identify(metrics)

    def plan_capacity(self, demand: Dict[str, Any]) -> Dict[str, Any]:
        return self._capacity.plan(demand)

    def get_metrics(self) -> Dict[str, Any]:
        return {"total_optimizations": self._optimization_count}
