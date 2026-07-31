"""Data models for pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStage:
    """A single stage inside a pipeline."""

    stage_id: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    next_on_success: str | None = None
    next_on_failure: str | None = None
    timeout: float | None = None


@dataclass
class PipelineDefinition:
    """A defined pipeline with ordered stages."""

    pipeline_id: str
    name: str
    description: str = ""
    stages: list[PipelineStage] = field(default_factory=list)
    on_failure: str = "stop"  # stop | continue
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "name": self.name,
            "description": self.description,
            "stages": [s.__dict__ for s in self.stages],
            "on_failure": self.on_failure,
            "version": self.version,
            "tags": list(self.tags),
        }


@dataclass
class PipelineRun:
    """Outcome of a single pipeline execution."""

    run_id: str
    pipeline_id: str
    status: str = "running"
    started_at: float | None = None
    finished_at: float | None = None
    stage_results: dict[str, Any] = field(default_factory=dict)
    stage_status: dict[str, str] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "pipeline_id": self.pipeline_id,
            "status": self.status,
            "stage_status": dict(self.stage_status),
            "error": self.error,
        }
