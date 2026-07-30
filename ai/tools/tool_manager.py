from __future__ import annotations

from typing import Any

from .tool_context import ToolContext
from .tool_events import ToolEvents
from .tool_executor import ToolExecutor
from .tool_logger import ToolLogger
from .tool_metrics import ToolMetrics
from .tool_permissions import ToolPermissions
from .tool_registry import ToolRegistry
from .tool_repository import ToolRepository
from .tool_runtime import ToolRuntime
from .tool_scheduler import ToolScheduler
from .tool_security import ToolSecurity
from .tool_validator import ToolValidator


class ToolManager:
    """Central manager composing all tool subsystems."""

    def __init__(self) -> None:
        self._registry = ToolRegistry()
        self._validator = ToolValidator(self._registry)
        self._metrics = ToolMetrics()
        self._logger = ToolLogger()
        self._executor = ToolExecutor(self._registry, self._validator, self._metrics, self._logger)
        self._permissions = ToolPermissions()
        self._security = ToolSecurity()
        self._context = ToolContext()
        self._runtime = ToolRuntime()
        self._scheduler = ToolScheduler()
        self._events = ToolEvents()
        self._repository = ToolRepository()

    @property
    def registry(self) -> ToolRegistry:
        return self._registry

    @property
    def executor(self) -> ToolExecutor:
        return self._executor

    @property
    def validator(self) -> ToolValidator:
        return self._validator

    @property
    def permissions(self) -> ToolPermissions:
        return self._permissions

    @property
    def security(self) -> ToolSecurity:
        return self._security

    @property
    def context(self) -> ToolContext:
        return self._context

    @property
    def runtime(self) -> ToolRuntime:
        return self._runtime

    @property
    def scheduler(self) -> ToolScheduler:
        return self._scheduler

    @property
    def events(self) -> ToolEvents:
        return self._events

    @property
    def metrics(self) -> ToolMetrics:
        return self._metrics

    @property
    def logger(self) -> ToolLogger:
        return self._logger

    @property
    def repository(self) -> ToolRepository:
        return self._repository

    def get_status(self) -> dict[str, Any]:
        return {
            "registered_tools": self._registry.tool_count,
            "active_contexts": self._context.active_count,
            "scheduled_tasks": self._scheduler.task_count,
            "total_calls": self._metrics.get_total_calls(),
            "total_errors": self._metrics.get_total_errors(),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "manager": "tool_manager",
            "status": self.get_status(),
            "registry": self._registry.to_dict(),
            "metrics": self._metrics.to_dict(),
        }
