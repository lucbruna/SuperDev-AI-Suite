from __future__ import annotations

import logging
from typing import Any

from .pipeline_builder import PipelineBuilder
from .pipeline_runner import PipelineRunner


class CICDEngine:
    """Continuous Integration / Continuous Delivery engine."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.cicd")
        self.builder = PipelineBuilder(self)
        self.runner = PipelineRunner(self)

    def run_pipeline(self, pipeline: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def get_status(self, pipeline_id: str) -> dict[str, Any]:
        raise NotImplementedError

    def list_pipelines(self) -> list[dict[str, Any]]:
        raise NotImplementedError
