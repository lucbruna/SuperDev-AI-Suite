from __future__ import annotations

import logging
import time
from typing import Any

from .workflow_models import WorkflowDefinition, WorkflowStatus
from .workflow_engine import WorkflowEngine
from .workflow_registry import WorkflowRegistry
from .workflow_config import WorkflowConfig
from .workflow_factory import WorkflowFactory
from .workflow_executor import WorkflowExecutor


class WorkflowManager:
    """High-level manager for workflow lifecycle."""

    def __init__(
        self,
        config: WorkflowConfig | None = None,
        registry: WorkflowRegistry | None = None,
    ) -> None:
        self._config = config or WorkflowConfig()
        self._registry = registry or WorkflowRegistry()
        self._engine = WorkflowEngine(config=self._config, registry=self._registry)
        self._executor = WorkflowExecutor()
        self._factory = WorkflowFactory()
        self._log = logging.getLogger("superdev.workflow.manager")

    def create_workflow(
        self, name: str, steps: list[dict[str, Any]] | None = None
    ) -> str:
        definition = self._factory.from_dict({
            "name": name,
            "steps": steps or [],
        })
        return self._engine.create(definition)

    def start_workflow(self, workflow_id: str) -> None:
        self._engine.start(workflow_id)

    def pause_workflow(self, workflow_id: str) -> None:
        self._engine.pause(workflow_id)

    def cancel_workflow(self, workflow_id: str) -> None:
        self._engine.cancel(workflow_id)

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        return self._registry.get(workflow_id)

    def list_workflows(self) -> list[WorkflowDefinition]:
        return self._registry.list_all()
