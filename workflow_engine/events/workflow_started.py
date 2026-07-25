from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class WorkflowStarted(BaseModel):
    workflow_id: str
    graph_id: str
    timestamp: datetime = None
    context: dict[str, Any] = {}

    def __init__(self, **data: Any) -> None:
        if "timestamp" not in data or data["timestamp"] is None:
            data["timestamp"] = datetime.now()
        super().__init__(**data)
