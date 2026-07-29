from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.graph.node import WorkflowNode
from workflow_engine.nodes.base_node import NodeResult


class ExecutionResult(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool = False
    output: Any = None
    node_results: list[NodeResult] = Field(default_factory=list)
    duration: float = 0.0
    error: str | None = None
    workflow_id: str = ""


class WorkflowExecutor:
    def __init__(self, registry: Any = None):
        self._registry = registry

    async def execute_graph(self, graph: WorkflowGraph, context: dict[str, Any], workflow_id: str) -> ExecutionResult:
        start = time.monotonic()
        sorted_nodes = graph.topological_sort()
        node_results: list[NodeResult] = []
        result = ExecutionResult(workflow_id=workflow_id)

        for node in sorted_nodes:
            nr = await self._execute_single_node(node, context)
            node_results.append(nr)
            if not nr.success:
                result.success = False
                result.error = nr.error
                result.node_results = node_results
                result.duration = time.monotonic() - start
                return result
            if nr.output is not None:
                context[node.id] = nr.output

        result.success = True
        result.node_results = node_results
        result.output = context.copy()
        result.duration = time.monotonic() - start
        return result

    async def _execute_single_node(self, node: WorkflowNode, context: dict[str, Any]) -> NodeResult:
        if self._registry:
            node_cls = self._registry.get_node_class(node.type.value)
            if node_cls is None:
                return NodeResult(node_id=node.id, status="failed", error=f"No registered class for node type {node.type}")
            instance = node_cls()
            instance.config = node.config
            return await instance.execute(context)
        from workflow_engine.executor.task_executor import TaskExecutor
        executor = TaskExecutor(self._registry)
        return await executor.execute_node(node.id, node, context)
