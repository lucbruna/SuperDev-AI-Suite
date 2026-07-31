"""Pipeline engine: facade for the pipelines subsystem."""

from __future__ import annotations

from typing import Any, Callable

from automation.pipelines.pipeline_builder import PipelineBuilder
from automation.pipelines.pipeline_executor import PipelineExecutor
from automation.pipelines.pipeline_history import PipelineHistory
from automation.pipelines.pipeline_models import PipelineDefinition, PipelineRun
from automation.pipelines.pipeline_validator import PipelineValidator


class PipelineEngine:
    """Registers and runs pipelines."""

    def __init__(self, validator: PipelineValidator | None = None,
                 executor: PipelineExecutor | None = None,
                 history: PipelineHistory | None = None,
                 events: Any = None, metrics: Any = None) -> None:
        self.validator = validator or PipelineValidator()
        self.history = history or PipelineHistory()
        self.events = events
        self.metrics = metrics
        self.executor = executor or PipelineExecutor(
            events=events, metrics=metrics)
        self._pipelines: dict[str, PipelineDefinition] = {}

    def build(self) -> PipelineBuilder:
        return PipelineBuilder()

    def register(self, pipeline: PipelineDefinition) -> list[str] | None:
        issues = self.validator.validate(pipeline)
        if issues:
            return issues
        self._pipelines[pipeline.pipeline_id] = pipeline
        return None

    def get(self, pipeline_id: str) -> PipelineDefinition | None:
        return self._pipelines.get(pipeline_id)

    def list(self) -> list[str]:
        return list(self._pipelines)

    def remove(self, pipeline_id: str) -> bool:
        return self._pipelines.pop(pipeline_id, None) is not None

    def register_action(self, action: str,
                        handler: Callable[[dict[str, Any]], Any]) -> None:
        self.executor.register_action(action, handler)

    def run(self, pipeline_id: str,
            variables: dict[str, Any] | None = None) -> PipelineRun | None:
        pipeline = self._pipelines.get(pipeline_id)
        if pipeline is None:
            return None
        run = self.executor.run(pipeline, variables)
        self.history.record(run)
        return run

    def run_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.history.list(limit)

    def stats(self) -> dict[str, int]:
        return {
            "registered": len(self._pipelines),
            "completed": self.history.count("completed"),
            "failed": self.history.count("failed"),
        }
