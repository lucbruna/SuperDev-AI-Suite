from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .pipeline_context import PipelineContext


@dataclass
class PipelineStage:
    name: str = ""
    action: str = ""
    config: dict[str, Any] = field(default_factory=dict)

    def run(self, context: PipelineContext) -> PipelineContext:
        try:
            result = self._execute_action(context)
            context.update(result)
        except Exception as exc:
            context.error = str(exc)
        return context

    def _execute_action(self, context: PipelineContext) -> dict[str, Any]:
        return {"stage": self.name, "status": "ok"}
