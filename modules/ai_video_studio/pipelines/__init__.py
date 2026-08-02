"""Base pipeline class — shared infrastructure for all video generation pipelines."""
from __future__ import annotations
import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class PipelineStatus(str, Enum):
    QUEUED = "queued"
    PLANNING = "planning"
    GENERATING = "generating"
    RENDERING = "rendering"
    POST_PROCESSING = "post_processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PipelineStep:
    name: str
    status: PipelineStatus = PipelineStatus.QUEUED
    progress: float = 0.0
    result: Any = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class PipelineResult:
    pipeline_id: str
    status: PipelineStatus
    output_path: str | None = None
    output_url: str | None = None
    duration: float = 0.0
    file_size_bytes: int = 0
    steps: list[PipelineStep] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    @property
    def progress(self) -> float:
        if not self.steps:
            return 0.0
        return sum(s.progress for s in self.steps) / len(self.steps)

    def to_dict(self) -> dict:
        return {
            "pipeline_id": self.pipeline_id,
            "status": self.status.value,
            "output_path": self.output_path,
            "output_url": self.output_url,
            "duration": self.duration,
            "file_size_bytes": self.file_size_bytes,
            "progress": self.progress,
            "metadata": self.metadata,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
        }


class BasePipeline(ABC):
    """Abstract base for all video generation pipelines.

    Subclasses implement ``plan()`` and ``execute_steps()``.
    The base class handles lifecycle, progress tracking, and error handling.
    """

    name: str = "base"

    def __init__(self) -> None:
        self.pipeline_id = str(uuid.uuid4())
        self.result = PipelineResult(pipeline_id=self.pipeline_id, status=PipelineStatus.QUEUED)
        self._cancelled = False

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Run the full pipeline: plan → execute → post-process → finalize."""
        try:
            self.result.status = PipelineStatus.PLANNING
            plan = await self.plan(**kwargs)
            self.result.steps = [PipelineStep(name=s) for s in plan]

            for step in self.result.steps:
                if self._cancelled:
                    self.result.status = PipelineStatus.CANCELLED
                    return self.result.to_dict()
                step.status = PipelineStatus.GENERATING
                step.started_at = datetime.now(timezone.utc)
                try:
                    step.result = await self.execute_step(step.name, plan, **kwargs)
                    step.status = PipelineStatus.COMPLETED
                    step.progress = 1.0
                    step.completed_at = datetime.now(timezone.utc)
                except Exception as e:
                    step.status = PipelineStatus.FAILED
                    step.error = str(e)
                    self.result.status = PipelineStatus.FAILED
                    self.result.error = str(e)
                    logger.error(f"Pipeline {self.name} step '{step.name}' failed: {e}")
                    return self.result.to_dict()

            self.result.status = PipelineStatus.COMPLETED
            self.result.completed_at = datetime.now(timezone.utc)
            return self.result.to_dict()

        except Exception as e:
            self.result.status = PipelineStatus.FAILED
            self.result.error = str(e)
            self.result.completed_at = datetime.now(timezone.utc)
            logger.error(f"Pipeline {self.name} failed: {e}")
            return self.result.to_dict()

    def cancel(self) -> None:
        self._cancelled = True

    @abstractmethod
    async def plan(self, **kwargs: Any) -> list[str]:
        """Return ordered step names for this pipeline."""
        ...

    @abstractmethod
    async def execute_step(self, step_name: str, plan: list[str], **kwargs: Any) -> Any:
        """Execute a single named step and return its result."""
        ...
