"""Fluent builder for pipeline definitions."""

from __future__ import annotations

from typing import Any

from automation.pipelines.pipeline_models import PipelineDefinition, PipelineStage


class PipelineBuilder:
    """Builds a PipelineDefinition step by step."""

    def __init__(self) -> None:
        self._pipeline = PipelineDefinition(pipeline_id="", name="")

    def id(self, pipeline_id: str) -> "PipelineBuilder":
        self._pipeline.pipeline_id = pipeline_id
        return self

    def name(self, name: str) -> "PipelineBuilder":
        self._pipeline.name = name
        return self

    def description(self, description: str) -> "PipelineBuilder":
        self._pipeline.description = description
        return self

    def on_failure(self, mode: str) -> "PipelineBuilder":
        self._pipeline.on_failure = mode
        return self

    def stage(self, stage_id: str, action: str,
              params: dict[str, Any] | None = None,
              next_on_success: str | None = None,
              next_on_failure: str | None = None,
              timeout: float | None = None) -> "PipelineBuilder":
        self._pipeline.stages.append(PipelineStage(
            stage_id=stage_id, action=action, params=params or {},
            next_on_success=next_on_success,
            next_on_failure=next_on_failure, timeout=timeout))
        return self

    def build(self) -> PipelineDefinition:
        return self._pipeline
