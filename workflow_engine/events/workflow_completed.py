from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class WorkflowCompleted(BaseModel):
    workflow_id: str
    status: str = "completed"
    duration_ms: float = 0.0
    result_summary: Optional[str] = None
