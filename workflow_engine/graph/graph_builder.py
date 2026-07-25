from __future__ import annotations

import json
from typing import Any

from workflow_engine.graph.edge import WorkflowEdge
from workflow_engine.graph.graph import WorkflowGraph
from workflow_engine.graph.node import NodeHandle, NodeType, WorkflowNode


class GraphBuilder:
    @staticmethod
    def from_dict(graph_data: dict[str, Any]) -> WorkflowGraph:
        graph = WorkflowGraph()
        for node_data in graph_data.get("nodes", []):
            handles_in = [NodeHandle(**h) for h in node_data.get("inputs", [])]
            handles_out = [NodeHandle(**h) for h in node_data.get("outputs", [])]
            node = WorkflowNode(
                id=node_data["id"],
                type=NodeType(node_data["type"]),
                name=node_data.get("name", node_data["id"]),
                config=node_data.get("config", {}),
                position=tuple(node_data.get("position", [0, 0])),
                description=node_data.get("description", ""),
                inputs=handles_in,
                outputs=handles_out,
                metadata=node_data.get("metadata", {}),
            )
            graph.add_node(node)
        for edge_data in graph_data.get("edges", []):
            edge = WorkflowEdge(
                id=edge_data.get("id", f"{edge_data['source']}->{edge_data['target']}"),
                source_node_id=edge_data["source"],
                target_node_id=edge_data["target"],
                source_handle=edge_data.get("source_handle", "default"),
                target_handle=edge_data.get("target_handle", "default"),
                condition=edge_data.get("condition"),
                label=edge_data.get("label", ""),
                metadata=edge_data.get("metadata", {}),
            )
            graph.add_edge(edge)
        graph.metadata = graph_data.get("metadata", {})
        return graph

    @staticmethod
    def from_json(json_str: str) -> WorkflowGraph:
        return GraphBuilder.from_dict(json.loads(json_str))

    @staticmethod
    def to_dict(graph: WorkflowGraph) -> dict[str, Any]:
        return {
            "id": graph.id,
            "nodes": [n.model_dump() for n in graph.nodes.values()],
            "edges": [e.model_dump() for e in graph.edges.values()],
            "metadata": graph.metadata,
        }

    @staticmethod
    def to_json(graph: WorkflowGraph) -> str:
        return json.dumps(GraphBuilder.to_dict(graph), indent=2, default=str)
