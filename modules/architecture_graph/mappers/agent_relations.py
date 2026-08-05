"""Agent relations: map how agents relate to files, plugins and workflows."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.edge_builder import contains, uses
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.mappers.agent_mapper import AgentMapper
from modules.architecture_graph.mappers.workflow_execution_map import (
    WorkflowExecutionMap,
)


class AgentRelations:
    """Build agent <-> file/plugin/workflow relations on the graph."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.mapper = AgentMapper(root)

    def apply(self, graph: ArchitectureGraph) -> int:
        """Wire agent nodes to their source files and referenced entities."""
        if not self.mapper.agents:
            self.mapper.discover()
        edges = 0

        # 1) agent -> own source file(s)
        for agent in self.mapper.agents:
            name = agent.get("name", "")
            rel_path = agent.get("path", "")
            if not name or not rel_path:
                continue
            agent_id = f"agent:{name}"
            if not graph.has_node(agent_id):
                continue
            file_id = f"file:{rel_path}"
            if graph.has_node(file_id):
                if graph.add_edge(contains(agent_id, file_id)):
                    edges += 1

        # 2) workflows referencing the agent
        executions = WorkflowExecutionMap(self.root).build().get("executions", {})
        for wf_name, execution in executions.items():
            wf_id = f"workflow:{wf_name}"
            if not graph.has_node(wf_id):
                continue
            for agent_name in execution.get("agents", []):
                agent_id = f"agent:{agent_name}"
                if graph.has_node(agent_id) and graph.add_edge(uses(wf_id, agent_id)):
                    edges += 1
        return edges

    def relations_of(self, agent_name: str) -> dict[str, Any]:
        """Human-readable relations for a single agent."""
        if not self.mapper.agents:
            self.mapper.discover()
        agent = self.mapper.get(agent_name)
        if agent is None:
            return {"found": False}
        executions = WorkflowExecutionMap(self.root).build().get("executions", {})
        workflows = [
            name for name, ex in executions.items() if agent_name in ex.get("agents", [])
        ]
        return {
            "found": True,
            "agent": agent,
            "workflows": workflows,
            "source_files": [agent.get("path")] if agent.get("path") else [],
        }
