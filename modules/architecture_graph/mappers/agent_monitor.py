"""Agent monitor: lightweight health/status aggregation for agents.

Static, graph-derived agent status: which agents exist, which workflows use
them and how connected they are. Useful for the dashboard's agent panel and
for Architecture Intelligence monitoring overlays.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.mappers.agent_mapper import AgentMapper


class AgentMonitor:
    """Aggregate agent connectivity and usage from the graph."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.mapper = AgentMapper(root)

    def report(self, graph: ArchitectureGraph) -> dict[str, Any]:
        if not self.mapper.agents:
            self.mapper.discover()
        rows: list[dict[str, Any]] = []
        for agent in self.mapper.agents:
            name = agent.get("name", "")
            agent_id = f"agent:{name}"
            node = graph.get_node(agent_id)
            dependents = len(graph.incoming(agent_id)) if node else 0
            dependencies = len(graph.outgoing(agent_id)) if node else 0
            rows.append(
                {
                    "name": name,
                    "id": agent_id,
                    "path": agent.get("path", ""),
                    "format": agent.get("format", ""),
                    "in_graph": node is not None,
                    "used_by": dependents,
                    "uses": dependencies,
                    "status": "active" if dependents > 0 else "unused",
                }
            )
        rows.sort(key=lambda r: (-r["used_by"], r["name"]))
        return {
            "total": len(rows),
            "in_graph": sum(1 for r in rows if r["in_graph"]),
            "active": sum(1 for r in rows if r["status"] == "active"),
            "unused": sum(1 for r in rows if r["status"] == "unused"),
            "agents": rows,
        }


def monitor_report(graph: ArchitectureGraph, root: str = "") -> dict[str, Any]:
    """One-shot convenience helper (root defaults to empty -> discovered)."""
    return AgentMonitor(root).report(graph)
