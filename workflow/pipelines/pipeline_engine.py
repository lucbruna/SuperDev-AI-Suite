from __future__ import annotations

import logging
from typing import Any

from .pipeline_models import Pipeline, PipelineStatus
from .pipeline_builder import PipelineBuilder
from .pipeline_executor import PipelineExecutor
from .pipeline_hooks import PipelineHooks
from .pipeline_events import PipelineEvents
from .pipeline_metrics import PipelineMetrics


class PipelineEngine:
    """Orchestrates pipeline execution lifecycle."""

    def __init__(self) -> None:
        self._builder = PipelineBuilder()
        self._executor = PipelineExecutor()
        self._hooks = PipelineHooks()
        self._events = PipelineEvents()
        self._metrics = PipelineMetrics()
        self._log = logging.getLogger("superdev.workflow.pipelines")

    def create_pipeline(self, name: str) -> Pipeline:
        return self._builder.build(name)

    def run_pipeline(self, pipeline: Pipeline) -> Pipeline:
        self._events.emit("pipeline.started", pipeline_id=pipeline.id)
        try:
            result = self._executor.execute(pipeline)
            pipeline.status = PipelineStatus.COMPLETED
            pipeline.context["result"] = result
            self._events.emit("pipeline.completed", pipeline_id=pipeline.id)
        except Exception as exc:
            pipeline.status = PipelineStatus.FAILED
            pipeline.error = str(exc)
            self._events.emit("pipeline.failed", pipeline_id=pipeline.id, error=str(exc))
            self._log.exception("Pipeline %s failed", pipeline.id)
        self._metrics.record_run(pipeline)
        self._hooks.run("after_pipeline", pipeline)
        return pipeline
