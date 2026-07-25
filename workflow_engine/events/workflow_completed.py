from __future__ import annotations

from pydantic import BaseModel


class WorkflowCompleted(BaseModel):
    workflow_id: str
    status: str = "completed"
    duration_ms: float = 0.0
    result_summary: str | None = None
