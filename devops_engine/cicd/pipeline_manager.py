"""CI/CD pipeline management (Volume 37, Fase 3)."""

from __future__ import annotations

from devops_engine.devops_models import Pipeline, PipelineStatus
from devops_engine.devops_protocols import new_id, now


class PipelineManager:
    """Defines and runs CI/CD pipelines."""

    def __init__(self) -> None:
        self._pipelines: dict[str, Pipeline] = {}

    def create(self, name: str,
               steps: list[str] | None = None) -> Pipeline:
        pipeline = Pipeline(
            pipeline_id=new_id("pipeline"),
            name=name,
            status=PipelineStatus.PENDING,
            steps=list(steps or []),
            created_at=now(),
        )
        self._pipelines[pipeline.pipeline_id] = pipeline
        return pipeline

    def start(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if pipeline is None:
            return False
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = now()
        return True

    def succeed(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if pipeline is None:
            return False
        pipeline.status = PipelineStatus.SUCCEEDED
        pipeline.finished_at = now()
        return True

    def fail(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if pipeline is None:
            return False
        pipeline.status = PipelineStatus.FAILED
        pipeline.finished_at = now()
        return True

    def cancel(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if pipeline is None:
            return False
        pipeline.status = PipelineStatus.CANCELLED
        return True

    def get(self, pipeline_id: str) -> Pipeline | None:
        return self._pipelines.get(pipeline_id)

    def list(self) -> list[Pipeline]:
        return list(self._pipelines.values())

    def count(self) -> int:
        return len(self._pipelines)
