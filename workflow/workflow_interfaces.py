from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .workflow_models import WorkflowDefinition, WorkflowStatus


class IWorkflowEngine(ABC):
    @abstractmethod
    def create(self, definition: WorkflowDefinition) -> str: ...
    @abstractmethod
    def start(self, workflow_id: str) -> None: ...
    @abstractmethod
    def pause(self, workflow_id: str) -> None: ...
    @abstractmethod
    def cancel(self, workflow_id: str) -> None: ...
    @abstractmethod
    def get_status(self, workflow_id: str) -> WorkflowStatus: ...


class IWorkflowExecutor(ABC):
    @abstractmethod
    def execute_step(self, step_id: str, context: dict[str, Any]) -> Any: ...
    @abstractmethod
    def can_execute(self, step_id: str) -> bool: ...
