from __future__ import annotations

from typing import Any

from .pipeline_models import Pipeline


class PipelineBuilder:
    """Builds pipeline configurations."""

    def __init__(self) -> None:
        self._stages: list[dict[str, Any]] = []

    def add_stage(self, name: str, action: str, config: dict[str, Any] | None = None) -> PipelineBuilder:
        self._stages.append({"name": name, "action": action, "config": config or {}})
        return self

    def build(self, name: str) -> Pipeline:
        return Pipeline(name=name, stages=list(self._stages))
