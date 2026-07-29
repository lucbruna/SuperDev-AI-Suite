from __future__ import annotations

import asyncio
from typing import Any

from workflow_engine.graph.node import NodeType
from workflow_engine.nodes.base_node import BaseNode, NodeResult


class ParallelNode(BaseNode):
    node_type: NodeType = NodeType.PARALLEL

    async def execute(self, context: dict[str, Any]) -> NodeResult:
        max_concurrency = self.config.get("max_concurrency", 5)
        fail_fast = self.config.get("fail_fast", False)
        child_nodes = self.config.get("child_nodes", [])
        semaphore = asyncio.Semaphore(max_concurrency)

        async def run_child(child: dict[str, Any]) -> NodeResult:
            async with semaphore:
                child_id = child.get("id", "")
                child_type = child.get("type", "")
                child_config = child.get("config", {})
                from workflow_engine.core.registry import WorkflowRegistry
                registry = WorkflowRegistry()
                node_cls = registry.get_node_class(child_type)
                if node_cls is None:
                    return NodeResult(node_id=child_id, status="failed", error=f"No class for type {child_type}")
                instance = node_cls()
                instance.config = child_config
                return await instance.execute(context)

        tasks = [run_child(c) for c in child_nodes]
        results: list[NodeResult] = []

        if fail_fast:
            for coro in asyncio.as_completed(tasks):
                nr = await coro
                results.append(nr)
                if not nr.success:
                    for t in tasks:
                        t.cancel()
                    return NodeResult(
                        node_id=self.config.get("node_id", ""),
                        status="failed",
                        error=f"Parallel child {nr.node_id} failed: {nr.error}",
                        output={"child_results": results},
                    )
        else:
            gathered = await asyncio.gather(*tasks, return_exceptions=True)
            for r in gathered:
                if isinstance(r, Exception):
                    results.append(NodeResult(node_id="", status="failed", error=str(r)))
                else:
                    results.append(r)

        all_success = all(nr.success for nr in results)
        return NodeResult(
            node_id=self.config.get("node_id", ""),
            status="success" if all_success else "failed",
            output={"child_results": [r.to_dict() for r in results]},
            error=None if all_success else "Some parallel children failed",
        )
