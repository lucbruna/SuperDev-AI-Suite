from __future__ import annotations

import asyncio
from typing import Any

from workflow_engine.graph.node import NodeType
from workflow_engine.nodes.base_node import BaseNode, NodeResult


class WaitNode(BaseNode):
    node_type: NodeType = NodeType.WAIT

    async def execute(self, context: dict[str, Any]) -> NodeResult:  # noqa: ARG002
        seconds = self.config.get("seconds", 1)
        await asyncio.sleep(seconds)
        return NodeResult(
            node_id=self.config.get("node_id", ""),
            status="success",
            output={"waited_seconds": seconds},
        )
