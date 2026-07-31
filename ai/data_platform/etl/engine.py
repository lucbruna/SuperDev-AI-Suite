"""ETL engine."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from .models import ETLStep, ETLPipeline, ETLLog, StepType, ETLStatus


class ETLEngine:
    def __init__(self):
        self._pipelines: Dict[str, ETLPipeline] = {}
        self._logs: List[ETLLog] = []

    def create_pipeline(self, pipeline: ETLPipeline) -> ETLPipeline:
        self._pipelines[pipeline.pipeline_id] = pipeline
        return pipeline

    def get_pipeline(self, pipeline_id: str) -> Optional[ETLPipeline]:
        return self._pipelines.get(pipeline_id)

    def add_step(self, pipeline_id: str, step: ETLStep) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        pipeline.steps.append(step)
        pipeline.steps.sort(key=lambda s: s.order)
        return True

    def start_pipeline(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        pipeline.status = ETLStatus.EXTRACTING
        pipeline.started_at = datetime.now()
        return True

    def complete_step(self, pipeline_id: str, step_id: str, records: int = 0) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        for step in pipeline.steps:
            if step.step_id == step_id:
                step.status = ETLStatus.COMPLETED
                if step.step_type == StepType.EXTRACT:
                    pipeline.records_extracted += records
                elif step.step_type == StepType.TRANSFORM:
                    pipeline.records_transformed += records
                elif step.step_type == StepType.LOAD:
                    pipeline.records_loaded += records
                return True
        return False

    def complete_pipeline(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        pipeline.status = ETLStatus.COMPLETED
        pipeline.completed_at = datetime.now()
        return True

    def fail_pipeline(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        pipeline.status = ETLStatus.FAILED
        pipeline.error_count += 1
        return True

    def add_log(self, log: ETLLog) -> ETLLog:
        self._logs.append(log)
        return log

    def get_logs(self, pipeline_id: Optional[str] = None) -> List[ETLLog]:
        if pipeline_id:
            return [l for l in self._logs if l.pipeline_id == pipeline_id]
        return list(self._logs)

    def get_stats(self) -> dict:
        pipelines = list(self._pipelines.values())
        return {
            "pipelines": len(pipelines),
            "completed": len([p for p in pipelines if p.status == ETLStatus.COMPLETED]),
            "failed": len([p for p in pipelines if p.status == ETLStatus.FAILED]),
            "total_extracted": sum(p.records_extracted for p in pipelines),
            "total_loaded": sum(p.records_loaded for p in pipelines),
        }
