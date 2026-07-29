from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from workflow_engine.events.workflow_completed import WorkflowCompleted


class WorkflowFinished(BaseModel):
    workflow_id: str
    status: str = "completed"
    duration: float = 0.0
    result: Any = None

    def to_completed(self) -> WorkflowCompleted:
        return WorkflowCompleted(
            workflow_id=self.workflow_id,
            status=self.status,
            duration_ms=self.duration * 1000,
            result_summary=str(self.result) if self.result else None,
        )
