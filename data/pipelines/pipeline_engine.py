from __future__ import annotations

import time
from typing import Any

from ..data_models import (
    PipelineDefinition,
    PipelineRun,
    PipelineRunStatus,
    PipelineStatus,
)


class PipelineEngine:
    """Data pipelines — DAG execution, scheduling, monitoring, recovery."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.pipelines
        self._definitions: dict[str, PipelineDefinition] = {}
        self._runs: dict[str, PipelineRun] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def create_pipeline(
        self,
        name: str,
        steps: list[dict[str, Any]],
        description: str = "",
        schedule: str = "",
    ) -> PipelineDefinition:
        definition = PipelineDefinition(
            name=name,
            description=description,
            steps=steps,
            schedule=schedule,
        )
        self._definitions[definition.pipeline_id] = definition
        self.engine.registry.register_pipeline(definition)
        return definition

    def get_pipeline(self, pipeline_id: str) -> PipelineDefinition | None:
        return self._definitions.get(pipeline_id)

    def list_pipelines(self) -> list[PipelineDefinition]:
        return list(self._definitions.values())

    def activate(self, pipeline_id: str) -> bool:
        definition = self._definitions.get(pipeline_id)
        if not definition:
            return False
        definition.status = PipelineStatus.ACTIVE
        return True

    async def run(self, pipeline_id: str) -> PipelineRun:
        definition = self._definitions.get(pipeline_id)
        if not definition:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        run = PipelineRun(pipeline_id=pipeline_id, status=PipelineRunStatus.RUNNING)
        self._runs[run.run_id] = run
        self.engine.runtime.begin_pipeline()
        self.engine.metrics.increment("pipelines.runs")

        try:
            for step in definition.steps:
                name = step.get("name", "step")
                run.steps_progress[name] = "running"
                await self._execute_step(step, run)
                run.steps_progress[name] = "succeeded"
            run.status = PipelineRunStatus.SUCCEEDED
        except Exception as exc:
            run.status = PipelineRunStatus.FAILED
            run.error = str(exc)
        finally:
            run.completed_at = time.time()
            self.engine.runtime.end_pipeline()
            await self.engine.event_bus.emit("data.pipeline_run", {
                "run_id": run.run_id,
                "pipeline_id": pipeline_id,
                "status": run.status.value,
            })

        return run

    async def _execute_step(self, step: dict[str, Any], run: PipelineRun) -> None:
        step_type = step.get("type", "")
        if step_type == "ingest":
            source = step.get("source", "default")
            config = step.get("config", {})
            await self.engine.ingestion.ingest(source, config)
        elif step_type == "process":
            # process most recent batch from the step's source
            source = step.get("source")
            if source:
                batches = self.engine.ingestion.recent_batches(source, limit=1)
                if batches:
                    await self.engine.processing.process_batch(batches[0])
        elif step_type == "etl":
            await self.engine.etl.run_job(step.get("job_id", ""))
        elif step_type == "notify":
            await self.engine.event_bus.emit("data.pipeline_notify", {"step": step})
        else:
            await self.engine.event_bus.emit("data.pipeline_step", {"step": step})

    def get_run(self, run_id: str) -> PipelineRun | None:
        return self._runs.get(run_id)

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "pipelines": len(self._definitions),
            "runs": len(self._runs),
        }


__all__ = ["PipelineEngine"]
