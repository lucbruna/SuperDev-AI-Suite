from __future__ import annotations

from typing import Any

from workflow_engine.graph.node import NodeType
from workflow_engine.nodes.base_node import BaseNode, NodeResult


class AgentNode(BaseNode):
    node_type: NodeType = NodeType.AGENT

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        pass
