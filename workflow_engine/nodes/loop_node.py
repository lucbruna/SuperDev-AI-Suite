from __future__ import annotations

import asyncio
from typing import Any

from workflow_engine.nodes.base_node import BaseNode, NodeResult
from workflow_engine.graph.node import NodeType


class LoopNode(BaseNode):
    node_type: NodeType = NodeType.LOOP

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        max_iterations = self.config.get("max_iterations", 10)
        condition_expr = self.config.get("condition_expr", "")
        child_nodes = self.config.get("child_nodes", [])

        iterations = 0
        all_outputs = []

        while iterations < max_iterations:
            if condition_expr:
                try:
                    should_continue = bool(eval(condition_expr, {"__builtins__": {}}, context))
                    if not should_continue:
                        break
                except Exception:
                    break

            for child in child_nodes:
                child_id = child.get("id", "")
                child_type = child.get("type", "")
                child_config = child.get("config", {})
                node_cls = None
                from workflow_engine.core.registry import WorkflowRegistry
                registry = WorkflowRegistry()
                node_cls = registry.get_node_class(child_type)
                if node_cls:
                    instance = node_cls()
                    instance.config = child_config
                    nr = await instance.execute(context)
                    all_outputs.append(nr)
                    if nr.output is not None:
                        context[child_id] = nr.output
                    if not nr.success:
                        return NodeResult(
                            node_id=self.config.get("node_id", ""),
                            status="failed",
                            error=f"Loop child {child_id} failed: {nr.error}",
                            output={"iterations": iterations, "child_results": all_outputs},
                        )

            iterations += 1

        return NodeResult(
            node_id=self.config.get("node_id", ""),
            status="success",
            output={"iterations": iterations, "child_results": all_outputs},
        )
