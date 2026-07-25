from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

from workflow_engine.graph.graph import WorkflowGraph


class ValidationError(BaseModel):
    code: str
    message: str
    node_id: Optional[str] = None
    edge_id: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool = True
    errors: list[ValidationError] = []
    warnings: list[str] = []


class GraphValidator:
    @staticmethod
    def validate(graph: WorkflowGraph) -> ValidationResult:
        result = ValidationResult()
        if not graph.nodes:
            result.is_valid = False
            result.errors.append(ValidationError(code="EMPTY_GRAPH", message="Graph must contain at least one node"))
            return result
        for nid, node in graph.nodes.items():
            if not node.id:
                result.is_valid = False
                result.errors.append(ValidationError(code="MISSING_NODE_ID", message="Node missing id", node_id=nid))
            if not node.type:
                result.is_valid = False
                result.errors.append(ValidationError(code="MISSING_NODE_TYPE", message=f"Node {nid} missing type", node_id=nid))
            if not node.name:
                result.warnings.append(f"Node {nid} has no name")
        for eid, edge in graph.edges.items():
            if edge.source_node_id not in graph.nodes:
                result.is_valid = False
                result.errors.append(ValidationError(code="INVALID_SOURCE", message=f"Edge {eid} source node {edge.source_node_id} not found", edge_id=eid))
            if edge.target_node_id not in graph.nodes:
                result.is_valid = False
                result.errors.append(ValidationError(code="INVALID_TARGET", message=f"Edge {eid} target node {edge.target_node_id} not found", edge_id=eid))
            if edge.source_node_id == edge.target_node_id:
                result.is_valid = False
                result.errors.append(ValidationError(code="SELF_LOOP", message=f"Edge {eid} is a self-loop", edge_id=eid))
        sorted_nodes = graph.topological_sort()
        if len(sorted_nodes) != len(graph.nodes):
            result.is_valid = False
            result.errors.append(ValidationError(code="CYCLE_DETECTED", message="Graph contains a cycle (DAG required)"))
        all_referenced = {e.source_node_id for e in graph.edges.values()} | {e.target_node_id for e in graph.edges.values()}
        orphaned = set(graph.nodes.keys()) - all_referenced
        if len(graph.nodes) > 1 and orphaned:
            for oid in orphaned:
                result.warnings.append(f"Node {oid} is orphaned (no connections)")
        return result