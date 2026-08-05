"""Workflow execution map: which workflows execute which steps/agents.

Builds an execution-oriented view (who runs what, in what order) from the
scanned workflow records, useful for orchestration monitoring and impact
analysis.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.mappers.workflow_mapper import WorkflowMapper


class WorkflowExecutionMap:
    """Execution-oriented workflow view."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.records: list[dict[str, Any]] = []
        self._executions: dict[str, dict[str, Any]] = {}

    def build(self) -> dict[str, Any]:
        mapper = WorkflowMapper(self.root)
        self.records = mapper.scan()
        self._executions = {}
        for record in self.records:
            name = record.get("name", "")
            if not name:
                continue
            steps = record.get("steps", [])
            agents = record.get("agents", [])
            self._executions[name] = {
                "workflow": name,
                "path": record.get("path", ""),
                "format": record.get("format", ""),
                "steps": steps,
                "step_count": len(steps),
                "agents": agents,
                "agent_count": len(agents),
                "execution_chain": [
                    *[f"step:{s}" for s in steps if s],
                    *[f"agent:{a}" for a in agents if a],
                ],
            }
        return {"total": len(self._executions), "executions": self._executions}

    def get(self, workflow_name: str) -> dict[str, Any] | None:
        if not self._executions:
            self.build()
        return self._executions.get(workflow_name)

    def agents_in(self, workflow_name: str) -> list[str]:
        execution = self.get(workflow_name)
        return list(execution.get("agents", [])) if execution else []

    def workflows_using_agent(self, agent_name: str) -> list[str]:
        if not self._executions:
            self.build()
        return [
            name
            for name, ex in self._executions.items()
            if agent_name in ex.get("agents", [])
        ]

    def summary(self) -> dict[str, Any]:
        if not self._executions:
            self.build()
        agent_usage: dict[str, int] = {}
        step_total = 0
        for ex in self._executions.values():
            step_total += ex["step_count"]
            for agent in ex.get("agents", []):
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
        top_agents = sorted(agent_usage.items(), key=lambda kv: kv[1], reverse=True)[:10]
        return {
            "total_workflows": len(self._executions),
            "total_steps": step_total,
            "distinct_agents": len(agent_usage),
            "top_agents": [{"agent": a, "workflows": c} for a, c in top_agents],
        }


def build_execution_map(root: str) -> dict[str, Any]:
    """One-shot convenience helper."""
    return WorkflowExecutionMap(root).build()
