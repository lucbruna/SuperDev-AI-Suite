from __future__ import annotations

from typing import Any, Callable, Protocol

from .workflow_models import WorkflowStep


class WorkflowCallback(Protocol):
    def __call__(self, step: WorkflowStep, result: Any) -> None: ...


class WorkflowHook(Protocol):
    def before_step(self, step: WorkflowStep) -> None: ...
    def after_step(self, step: WorkflowStep, result: Any) -> None: ...
    def on_error(self, step: WorkflowStep, error: Exception) -> None: ...
