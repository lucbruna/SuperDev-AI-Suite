"""Workflow graph: build a focused subgraph for workflow orchestration.

Wraps the workflow records into a standalone graph (workflows, agents, steps,
plugins, services) so callers can inspect orchestration topology without the
full file-level graph.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.edge_builder import depends_on, uses
from modules.architecture_graph.graph.graph_builder import (
    ArchitectureGraph,
    GraphEdge,
    GraphNode,
)
from modules.architecture_graph.graph.node_builder import workflow_node
from modules.architecture_graph.mappers.workflow_mapper import WorkflowMapper


class WorkflowGraph:
    """Focused orchestration graph over workflows and their dependencies."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.graph = ArchitectureGraph(name="workflows", project_root=root)

    def build(self) -> ArchitectureGraph:
        mapper = WorkflowMapper(self.root)
        records = mapper.scan()
        added: set[str] = set()
        for record in records:
            name = record.get("name", "")
            if not name:
                continue
            wf_id = f"workflow:{name}"
            node = workflow_node(name, record.get("path", ""))
            node.meta = {"format": record.get("format", "")}
            self.graph.add_node(node)
            added.add(wf_id)
            for agent in record.get("agents", []):
                if not agent:
                    continue
                agent_id = f"agent:{agent}"
                if not self.graph.has_node(agent_id):
                    self.graph.add_node(
                        GraphNode(id=agent_id, name=agent, kind="agent", path=f"agents/{agent}/")
                    )
                self.graph.add_edge(uses(wf_id, agent_id))
            for step in record.get("steps", []):
                if not step:
                    continue
                step_id = f"step:{name}/{step}"
                self.graph.add_node(
                    GraphNode(id=step_id, name=step, kind="workflow", path=record.get("path", ""))
                )
                self.graph.add_edge(depends_on(wf_id, step_id))
        return self.graph

    def to_dict(self) -> dict[str, Any]:
        return self.graph.to_dict()


def build_workflow_graph(root: str) -> ArchitectureGraph:
    """One-shot convenience helper."""
    return WorkflowGraph(root).build()
