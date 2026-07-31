from __future__ import annotations

from typing import Any

from .automation_library import AutomationLibrary
from .decision_patterns import DecisionPatterns
from .execution_patterns import ExecutionPatterns
from .optimization_patterns import OptimizationPatterns
from .reusable_tasks import ReusableTasks
from .strategy_repository import StrategyRepository
from .workflow_repository import WorkflowRepository


class ProceduralMemory:
    """High-level facade for procedural memory — how to execute tasks."""

    def __init__(self):
        self._workflows = WorkflowRepository()
        self._patterns = ExecutionPatterns()
        self._tasks = ReusableTasks()
        self._automation = AutomationLibrary()
        self._strategies = StrategyRepository()
        self._optimizations = OptimizationPatterns()
        self._decisions = DecisionPatterns()

    @property
    def workflows(self) -> WorkflowRepository:
        return self._workflows

    @property
    def patterns(self) -> ExecutionPatterns:
        return self._patterns

    @property
    def tasks(self) -> ReusableTasks:
        return self._tasks

    @property
    def automation(self) -> AutomationLibrary:
        return self._automation

    @property
    def strategies(self) -> StrategyRepository:
        return self._strategies

    @property
    def optimizations(self) -> OptimizationPatterns:
        return self._optimizations

    @property
    def decisions(self) -> DecisionPatterns:
        return self._decisions

    def snapshot(self) -> dict[str, Any]:
        return {
            "workflows": self._workflows.count,
            "patterns": self._patterns.count,
            "reusable_tasks": self._tasks.count,
            "automation_scripts": self._automation.count,
            "strategies": self._strategies.count,
            "optimization_patterns": self._optimizations.count,
            "decision_patterns": self._decisions.count,
        }
