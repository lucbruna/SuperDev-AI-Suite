from __future__ import annotations

from typing import Any

from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.graph.node import WorkflowNode
from workflow_engine.nodes.base_node import NodeResult


class TaskExecutor:
    def __init__(self, registry: Any = None):
        self._registry = registry

    async def execute_node(self, node_id: str, graph: WorkflowGraph, context: dict[str, Any]) -> NodeResult:
        node = graph.get_node(node_id)
        if node is None:
            return NodeResult(node_id=node_id, status="failed", error=f"Node {node_id} not found in graph")

        node_cls = None
        if self._registry:
            node_cls = self._registry.get_node_class(node.type.value)

        if node_cls is None:
            return NodeResult(node_id=node_id, status="failed", error=f"No registered class for node type {node.type}")

        instance = node_cls()
        instance.config = node.config
        return await instance.execute(context)

    async def execute_node_direct(self, node: WorkflowNode, context: dict[str, Any]) -> NodeResult:
        node_cls = None
        if self._registry:
            node_cls = self._registry.get_node_class(node.type.value)

        if node_cls is None:
            return NodeResult(node_id=node.id, status="failed", error=f"No registered class for node type {node.type}")

        instance = node_cls()
        return await instance.execute(context)
