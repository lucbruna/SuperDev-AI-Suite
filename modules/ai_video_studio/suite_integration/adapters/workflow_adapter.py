"""Workflow adapter — register studio pipelines as suite workflows.

Bridges to ``SuperDev.workflow``: a studio pipeline (plan → render →
export) is registered as a first-class suite workflow definition, so the
platform orchestrator can schedule and run studio work.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.suite_integration.adapters.base import (
    SuiteAdapter,
    ensure_suite_importable,
    import_optional,
)

STUDIO_PIPELINE = ("plan", "generate", "render", "export")
PIPELINE_NAME = "ai_video_studio_pipeline"


class WorkflowAdapter(SuiteAdapter):
    """Suite workflow registration for studio pipelines."""

    name = "workflow"
    description = "Register studio pipelines as suite workflows (SuperDev.workflow)"
    platform_module = "SuperDev.workflow"
    actions = ("register_pipeline", "list_workflows")

    def __init__(self) -> None:
        super().__init__()
        self._workflow_ids: list[str] = []

    def register_pipeline(
        self,
        *,
        name: str = PIPELINE_NAME,
        steps: tuple[str, ...] = STUDIO_PIPELINE,
    ) -> dict[str, Any]:
        """Create a suite workflow for a studio pipeline."""
        ensure_suite_importable()
        wf = import_optional("SuperDev.workflow")
        if wf is None:
            return {"registered": False, "platform": False,
                    "error": "suite workflow engine unavailable"}
        try:
            engine = wf.WorkflowEngine()
            definition = wf.WorkflowFactory().create_simple(name, list(steps))
            workflow_id = engine.create(definition)
            self._workflow_ids.append(workflow_id)
            return {
                "registered": True,
                "workflow_id": workflow_id,
                "name": name,
                "steps": list(steps),
                "platform": True,
            }
        except Exception as e:  # noqa: BLE001 — registration must not raise
            self._error = f"workflow registration failed: {e}"
            return {"registered": False, "platform": True, "error": self._error}

    def list_workflows(self) -> dict[str, Any]:
        """Ids of workflows registered by this adapter."""
        return {"workflow_ids": list(self._workflow_ids), "platform": self.available()}
