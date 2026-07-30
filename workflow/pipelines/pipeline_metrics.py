from __future__ import annotations

import time
from typing import Any

from .pipeline_models import Pipeline


class PipelineMetrics:
    """Tracks pipeline execution metrics."""

    def __init__(self) -> None:
        self._runs: list[dict[str, Any]] = []

    def record_run(self, pipeline: Pipeline) -> None:
        self._runs.append({
            "pipeline_id": pipeline.id,
            "name": pipeline.name,
            "status": pipeline.status.value,
            "timestamp": time.time(),
            "stages": len(pipeline.stages),
        })

    @property
    def total_runs(self) -> int:
        return len(self._runs)

    @property
    def success_rate(self) -> float:
        if not self._runs:
            return 0.0
        succeeded = sum(1 for r in self._runs if r["status"] == "completed")
        return succeeded / len(self._runs)
