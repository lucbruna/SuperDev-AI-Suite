from __future__ import annotations

import asyncio
from typing import Any

from workflow_engine.nodes.base_node import BaseNode, NodeResult
from workflow_engine.graph.node import NodeType


class ApprovalNode(BaseNode):
    node_type: NodeType = NodeType.APPROVAL

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        message = self.config.get("message", "Approve this step?")
        timeout = self.config.get("timeout", 3600)
        node_id = self.config.get("node_id", "")

        approval_key = f"approval_{node_id}"
        context[approval_key] = {"status": "pending", "message": message}

        try:
            async with asyncio.timeout(timeout):
                while context.get(approval_key, {}).get("status") == "pending":
                    await asyncio.sleep(1)
        except TimeoutError:
            return NodeResult(
                node_id=node_id,
                status="failed",
                error=f"Approval timed out after {timeout}s",
            )

        approval_status = context.get(approval_key, {}).get("status", "rejected")
        if approval_status != "approved":
            return NodeResult(
                node_id=node_id,
                status="failed",
                error=f"Approval rejected: {approval_status}",
            )

        return NodeResult(
            node_id=node_id,
            status="success",
            output={"approved": True, "message": message},
        )
