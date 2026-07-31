from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cicd_engine import CICDEngine

from .workflow import CICDWorkflow


class PipelineBuilder:
    """Builds CI/CD pipeline configurations."""

    def __init__(self, engine: CICDEngine) -> None:
        self._engine = engine
        self._pipelines: dict[str, CICDWorkflow] = {}
        self._meta: dict[str, dict[str, Any]] = {}

    def create(self, name: str, stages: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Create a pipeline from a list of stage dicts ({name, type, config})."""
        pipeline_id = f"pipe-{uuid.uuid4().hex[:8]}"
        workflow = CICDWorkflow(name)
        for stage in stages or []:
            workflow.add_stage(stage)
        errors = workflow.validate()
        if errors:
            raise ValueError(f"invalid pipeline: {', '.join(errors)}")
        self._pipelines[pipeline_id] = workflow
        self._meta[pipeline_id] = {"created_at": time.time()}
        self._engine._persist()
        return self.get(pipeline_id)

    def add_stage(self, pipeline: str, stage: dict[str, Any]) -> None:
        workflow = self._require(pipeline)
        workflow.add_stage(stage)
        self._engine._persist()

    def remove_stage(self, pipeline: str, stage_name: str) -> None:
        workflow = self._require(pipeline)
        workflow.remove_stage(stage_name)
        self._engine._persist()

    def get(self, pipeline_id: str) -> dict[str, Any]:
        workflow = self._require(pipeline_id)
        return {
            "pipeline_id": pipeline_id,
            "name": workflow.name,
            "stages": list(workflow.stages),
            "created_at": self._meta.get(pipeline_id, {}).get("created_at"),
        }

    def list(self) -> list[dict[str, Any]]:
        return [self.get(pid) for pid in self._pipelines]

    def _require(self, pipeline_id: str) -> CICDWorkflow:
        workflow = self._pipelines.get(pipeline_id)
        if workflow is None:
            raise KeyError(f"pipeline not found: {pipeline_id}")
        return workflow

    # -- persistence ---------------------------------------------------------

    def snapshot_state(self) -> dict[str, Any]:
        """Serialize pipeline definitions (workflows + metadata) for JSON."""
        return {
            pipeline_id: {
                "name": workflow.name,
                "stages": list(workflow.stages),
                "created_at": self._meta.get(pipeline_id, {}).get("created_at"),
            }
            for pipeline_id, workflow in self._pipelines.items()
        }

    def restore_state(self, data: dict[str, Any]) -> None:
        """Restore pipeline definitions from persisted JSON (tolerant of bad shapes)."""
        for pipeline_id, spec in data.items():
            if not isinstance(pipeline_id, str) or not isinstance(spec, dict):
                continue
            name = spec.get("name")
            stages = spec.get("stages")
            if not isinstance(name, str) or not isinstance(stages, list):
                continue
            workflow = CICDWorkflow(name)
            for stage in stages:
                if isinstance(stage, dict):
                    workflow.add_stage(stage)
            self._pipelines[pipeline_id] = workflow
            created_at = spec.get("created_at")
            if isinstance(created_at, (int, float)):
                self._meta[pipeline_id] = {"created_at": created_at}
