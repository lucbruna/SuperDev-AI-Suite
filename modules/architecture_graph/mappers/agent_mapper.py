"""Agent mapper: discover agent definitions and register them on the graph."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.graph.node_builder import agent_node

_AGENT_DIRS = ("agents", "core/agents", "agent_orchestration", "collaboration")


def _discover_agents(root: str) -> list[dict[str, Any]]:
    """Find agent definition files (yaml/json/py) and return normalized records."""
    base = Path(root)
    agents: list[dict[str, Any]] = []
    seen: set[str] = set()
    dirs = [base / d for d in _AGENT_DIRS if (base / d).exists()]
    for directory in dirs:
        for entry in sorted(directory.rglob("*")):
            if entry.suffix not in {".yaml", ".yml", ".json", ".py"}:
                continue
            if any(p in {".git", "node_modules", "__pycache__"} for p in entry.parts):
                continue
            rel = entry.relative_to(base).as_posix()
            if rel in seen:
                continue
            seen.add(rel)
            name = entry.stem
            agents.append(
                {
                    "name": name,
                    "path": rel,
                    "format": entry.suffix.lstrip("."),
                }
            )
    agents.sort(key=lambda a: a["path"])
    return agents


class AgentMapper:
    """Maps agent definitions onto the architecture graph."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.agents: list[dict[str, Any]] = []

    def discover(self) -> list[dict[str, Any]]:
        self.agents = _discover_agents(self.root)
        return self.agents

    def apply(self, graph: ArchitectureGraph) -> int:
        """Add agent nodes. Returns number of agents added."""
        if not self.agents:
            self.discover()
        added = 0
        for agent in self.agents:
            name = agent.get("name", "")
            if not name:
                continue
            node_id = f"agent:{name}"
            if not graph.has_node(node_id):
                node = agent_node(name, agent.get("path", ""))
                node.meta = {"format": agent.get("format", "")}
                graph.add_node(node)
                added += 1
        return added

    def get(self, name: str) -> dict[str, Any] | None:
        if not self.agents:
            self.discover()
        for agent in self.agents:
            if agent.get("name") == name:
                return agent
        return None

    def summary(self) -> dict[str, Any]:
        if not self.agents:
            self.discover()
        formats: dict[str, int] = {}
        for agent in self.agents:
            fmt = agent.get("format", "?")
            formats[fmt] = formats.get(fmt, 0) + 1
        return {"total": len(self.agents), "by_format": formats}


def discover_agents(root: str) -> list[dict[str, Any]]:
    """One-shot convenience helper."""
    return _discover_agents(root)
