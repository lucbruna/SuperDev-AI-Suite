from __future__ import annotations

import logging
from typing import Any

from .pipeline_models import Pipeline, PipelineStatus
from .pipeline_stage import PipelineStage
from .pipeline_context import PipelineContext


class PipelineExecutor:
    """Executes pipeline stages sequentially."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.workflow.pipelines.executor")

    def execute(self, pipeline: Pipeline) -> dict[str, Any]:
        pipeline.status = PipelineStatus.RUNNING
        context = PipelineContext(pipeline.context)
        for stage_cfg in pipeline.stages:
            stage = PipelineStage(**stage_cfg)
            context = stage.run(context)
            if context.error:
                pipeline.status = PipelineStatus.FAILED
                pipeline.error = context.error
                break
        if pipeline.status == PipelineStatus.RUNNING:
            pipeline.status = PipelineStatus.COMPLETED
        return context.data
