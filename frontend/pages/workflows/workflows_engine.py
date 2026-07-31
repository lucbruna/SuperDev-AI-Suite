from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class WorkflowsEngine:
    """Renders the workflows orchestration page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.workflows")
        self._context = context or FrontendContext()
        self._workflows: dict[str, dict[str, Any]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "workflows",
            "count": len(self._workflows),
            "workflows": self.list(),
        }

    def list(self) -> list[dict[str, Any]]:
        return [
            {"workflow_id": workflow_id, **workflow}
            for workflow_id, workflow in self._workflows.items()
        ]

    def create(self, name: str, definition: dict[str, Any]) -> str:
        workflow_id = f"workflow-{len(self._workflows) + 1}"
        self._workflows[workflow_id] = {
            "name": name,
            "definition": definition,
            "status": "draft",
            "created_at": time.time(),
        }
        return workflow_id

    def run(self, workflow_id: str) -> dict[str, Any]:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            raise KeyError(f"unknown workflow: {workflow_id}")
        workflow["status"] = "running"
        return {"workflow_id": workflow_id, "status": "running", "started_at": time.time()}

    def stop(self, workflow_id: str) -> bool:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            return False
        workflow["status"] = "stopped"
        return True

    def status(self, workflow_id: str) -> dict[str, Any]:
        workflow = self._workflows.get(workflow_id)
        if workflow is None:
            raise KeyError(f"unknown workflow: {workflow_id}")
        return {"workflow_id": workflow_id, **workflow}
