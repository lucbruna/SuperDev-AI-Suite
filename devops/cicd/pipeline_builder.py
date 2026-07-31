from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cicd_engine import CICDEngine


class PipelineBuilder:
    """Builds CI/CD pipeline configurations."""

    def __init__(self, engine: CICDEngine) -> None:
        self._engine = engine

    def create(self, name: str, stages: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def add_stage(self, pipeline: str, stage: dict[str, Any]) -> None:
        raise NotImplementedError

    def remove_stage(self, pipeline: str, stage_name: str) -> None:
        raise NotImplementedError
