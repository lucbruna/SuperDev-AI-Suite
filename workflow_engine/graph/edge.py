from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class WorkflowEdge(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    source_handle: str = "default"
    target_handle: str = "default"
    condition: Optional[str] = None
    label: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)