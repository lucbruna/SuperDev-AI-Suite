from __future__ import annotations

from typing import Any, Optional
from datetime import datetime

from workflow_engine.graph.node import NodeType


class NodeResult:
    def __init__(
        self,
        node_id: str,
        status: str,
        output: Any = None,
        error: Optional[str] = None,
        duration: float = 0.0,
    ):
        self.node_id = node_id
        self.status = status
        self.output = output
        self.error = error
        self.duration = duration

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "duration": self.duration,
        }


class BaseNode:
    node_type: NodeType = NodeType.TOOL

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        raise NotImplementedError