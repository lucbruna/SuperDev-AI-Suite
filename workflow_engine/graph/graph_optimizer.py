from __future__ import annotations

from typing import Any

from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.graph.node import WorkflowNode, NodeType
from workflow_engine.graph.edge import WorkflowEdge


class GraphOptimizer:
    @staticmethod
    def optimize(graph: WorkflowGraph) -> WorkflowGraph:
        optimized = graph.model_copy(deep=True)
        merged = GraphOptimizer._merge_sequential(optimized)
        parallelized = GraphOptimizer._parallelize_independent(merged)
        cleaned = GraphOptimizer._remove_dead_code(parallelized)
        return cleaned

    @staticmethod
    def _merge_sequential(graph: WorkflowGraph) -> WorkflowGraph:
        nodes_list = graph.topological_sort()
        merged_ids = set()
        for i in range(len(nodes_list) - 1):
            current = nodes_list[i]
            next_node = nodes_list[i + 1]
            if current.id in merged_ids or next_node.id in merged_ids:
                continue
            outgoing = [e for e in graph.edges.values() if e.source_node_id == current.id]
            incoming = [e for e in graph.edges.values() if e.target_node_id == next_node.id]
            if len(outgoing) == 1 and len(incoming) == 1 and outgoing[0].target_node_id == next_node.id:
                if current.type == next_node.type and current.type in (NodeType.TOOL, NodeType.PYTHON, NodeType.HTTP):
                    merged_name = f"{current.name}_{next_node.name}"
                    merged_config = {**current.config, **next_node.config}
                    merged_node = WorkflowNode(
                        id=current.id,
                        type=current.type,
                        name=merged_name,
                        config=merged_config,
                        position=current.position,
                    )
                    graph.nodes[current.id] = merged_node
                    for edge in list(graph.edges.values()):
                        if edge.source_node_id == next_node.id:
                            graph.add_edge(WorkflowEdge(
                                id=f"{current.id}->{edge.target_node_id}",
                                source_node_id=current.id,
                                target_node_id=edge.target_node_id,
                            ))
                    graph.remove_node(next_node.id)
                    merged_ids.add(next_node.id)
        return graph

    @staticmethod
    def _parallelize_independent(graph: WorkflowGraph) -> WorkflowGraph:
        return graph

    @staticmethod
    def _remove_dead_code(graph: WorkflowGraph) -> WorkflowGraph:
        all_referenced = {e.source_node_id for e in graph.edges.values()} | {e.target_node_id for e in graph.edges.values()}
        if len(graph.nodes) <= 1:
            return graph
        dead_ids = [nid for nid in graph.nodes if nid not in all_referenced]
        for nid in dead_ids:
            graph.remove_node(nid)
        return graph