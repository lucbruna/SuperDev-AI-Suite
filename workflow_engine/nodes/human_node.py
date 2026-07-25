from __future__ import annotations

import asyncio
from typing import Any

from workflow_engine.graph.node import NodeType
from workflow_engine.nodes.base_node import BaseNode, NodeResult


class HumanNode(BaseNode):
    node_type: NodeType = NodeType.HUMAN

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        prompt = self.config.get("prompt", "Enter input:")
        input_type = self.config.get("type", "text")
        node_id = self.config.get("node_id", "")

        input_key = f"human_input_{node_id}"
        context[input_key] = {"status": "pending", "prompt": prompt, "type": input_type}

        while context.get(input_key, {}).get("status") == "pending":
            await asyncio.sleep(1)

        user_input = context.get(input_key, {}).get("value", "")

        return NodeResult(
            node_id=node_id,
            status="success",
            output={"prompt": prompt, "input": user_input, "type": input_type},
        )
