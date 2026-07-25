from __future__ import annotations

from pydantic import BaseModel


class WorkflowFailed(BaseModel):
    workflow_id: str
    error_message: str = ""
    failed_node_id: str | None = None
    retry_count: int = 0
