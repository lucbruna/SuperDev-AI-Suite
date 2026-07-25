from __future__ import annotations

from typing import Any

from workflow_engine.nodes.base_node import BaseNode, NodeResult
from workflow_engine.graph.node import NodeType


class ToolNode(BaseNode):
    node_type: NodeType = NodeType.TOOL

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        tool_name = self.config.get("tool_name", "")
        params = self.config.get("params", {})
        resolved_params = {}
        for k, v in params.items():
            if isinstance(v, str) and v.startswith("$"):
                resolved_params[k] = context.get(v[1:], v)
            else:
                resolved_params[k] = v
        return NodeResult(
            node_id=self.config.get("node_id", ""),
            status="success",
            output={"tool": tool_name, "params": resolved_params, "result": f"Executed {tool_name}"},
        )
