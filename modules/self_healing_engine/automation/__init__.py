"""Automation: scheduled maintenance and continuous validation tasks."""
from __future__ import annotations

from modules.self_healing_engine.automation.tasks import (
    AutomationRunner,
    AutomationTask,
    CleanupTask,
    ContinuousValidationTask,
    OptimizationTask,
)

__all__ = [
    "AutomationRunner",
    "AutomationTask",
    "CleanupTask",
    "ContinuousValidationTask",
    "OptimizationTask",
]
