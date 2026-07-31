"""Pipeline orchestrator engine.

Builds pipelines from ``PipelineSpec`` objects and runs their stages in
sequence, tracking status, timing and events.
"""

from __future__ import annotations

from typing import Any

from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import PipelineSpec, PipelineStatus
from data_intelligence.data_protocols import new_id
from data_intelligence.pipelines.base import PipelineError, PipelineStage
from data_intelligence.pipelines.cleaning import CleaningStage
from data_intelligence.pipelines.extraction import ExtractionStage
from data_intelligence.pipelines.indicator import IndicatorStage
from data_intelligence.pipelines.sink import SinkStage
from data_intelligence.pipelines.transformation import TransformationStage

STAGE_REGISTRY: dict[str, type[PipelineStage]] = {
    "extraction": ExtractionStage,
    "cleaning": CleaningStage,
    "transformation": TransformationStage,
    "indicator": IndicatorStage,
    "sink": SinkStage,
}


class PipelineOrchestrator:
    """Pipeline engine attached by the facade as ``pipeline``."""

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.specs: dict[str, PipelineSpec] = {}
        self.results: dict[str, dict[str, Any]] = {}
        self.run_history: list[dict[str, Any]] = []

    # -- registration ------------------------------------------------------
    def register(self, spec: PipelineSpec) -> None:
        self.specs[spec.pipeline_id] = spec

    def add_pipeline(self, pipeline_id: str, name: str,
                     stages: list[dict[str, Any]],
                     schedule_cron: str | None = None) -> PipelineSpec:
        spec = PipelineSpec(pipeline_id=pipeline_id, name=name,
                            stages=stages, schedule_cron=schedule_cron)
        self.register(spec)
        return spec

    def remove(self, pipeline_id: str) -> bool:
        self.results.pop(pipeline_id, None)
        return self.specs.pop(pipeline_id, None) is not None

    # -- stage building ----------------------------------------------------
    def build_stage(self, stage: dict[str, Any]) -> PipelineStage:
        stage_type = stage.get("stage", "cleaning")
        klass = STAGE_REGISTRY.get(stage_type)
        if klass is None:
            raise PipelineError(f"unknown stage type: {stage_type}")
        config = {k: v for k, v in stage.items() if k != "stage"}
        return klass(**config)

    # -- execution ---------------------------------------------------------
    def run(self, pipeline_id: str,
            records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Runs a registered pipeline and returns a summary."""
        spec = self.specs.get(pipeline_id)
        if spec is None:
            raise PipelineError(f"unknown pipeline: {pipeline_id}")
        if not spec.enabled:
            return {"pipeline_id": pipeline_id, "status": "skipped"}
        run_id = new_id("run")
        self.events.publish(DataIntelligenceEventType.PIPELINE_STARTED,
                            {"pipeline_id": pipeline_id, "run_id": run_id})
        current = list(records or [])
        context: dict[str, Any] = {"pipeline_id": pipeline_id}
        with self.metrics.timed(f"pipeline.{pipeline_id}"):
            try:
                for stage_cfg in spec.stages:
                    stage = self.build_stage(stage_cfg)
                    current, context = stage.run(current, context)
                status = PipelineStatus.COMPLETED
            except PipelineError as exc:
                status = PipelineStatus.FAILED
                context["error"] = str(exc)
                self.events.publish(
                    DataIntelligenceEventType.PIPELINE_FAILED,
                    {"pipeline_id": pipeline_id, "error": str(exc)})
        result = {"pipeline_id": pipeline_id, "run_id": run_id,
                  "status": status.value, "output_count": len(current),
                  "context": context}
        self.results[pipeline_id] = result
        self.run_history.append(result)
        self.events.publish(DataIntelligenceEventType.PIPELINE_COMPLETED,
                            {"pipeline_id": pipeline_id,
                             "status": status.value})
        return result

    def run_all(self) -> list[dict[str, Any]]:
        return [self.run(pid) for pid in self.specs]

    def latest(self, pipeline_id: str) -> dict[str, Any] | None:
        return self.results.get(pipeline_id)

    def stats(self) -> dict[str, Any]:
        return {"pipelines": list(self.specs),
                "runs": len(self.run_history),
                "last_status": {pid: r["status"]
                                for pid, r in self.results.items()}}
