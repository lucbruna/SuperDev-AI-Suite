from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class WorkflowFailed(BaseModel):
    workflow_id: str
    error_message: str = ""
    failed_node_id: Optional[str] = None
    retry_count: int = 0
