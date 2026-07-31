from __future__ import annotations

from typing import Any


class GraphBuilder:
    """Base helpers for building typed graphs."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._nodes: list[dict[str, Any]] = []
        self._edges: list[dict[str, Any]] = []

    def add_node(self, node_id: str, label: str = "", kind: str = "node", **attrs: Any) -> None:
        self._nodes.append({"id": node_id, "label": label or node_id, "kind": kind, **attrs})

    def add_edge(self, source: str, target: str, kind: str = "depends_on", **attrs: Any) -> None:
        self._edges.append({"source": source, "target": target, "kind": kind, **attrs})

    def build(self) -> dict[str, Any]:
        return {"name": self.name, "nodes": self._nodes, "edges": self._edges}

    def count(self) -> dict[str, int]:
        return {"nodes": len(self._nodes), "edges": len(self._edges)}


class ArchitectureGraph(GraphBuilder):
    """Graph of system architecture components."""

    def __init__(self, name: str = "architecture") -> None:
        super().__init__(name)

    def add_module(self, module_id: str, label: str = "", layer: str = "core") -> None:
        self.add_node(module_id, label, kind="module", layer=layer)


class DependencyGraph(GraphBuilder):
    """Graph of dependency relationships between packages/modules."""

    def __init__(self, name: str = "dependencies") -> None:
        super().__init__(name)

    def add_dependency(self, source: str, target: str) -> None:
        self.add_edge(source, target, kind="imports")


class WorkflowGraph(GraphBuilder):
    """Graph of workflow steps and transitions."""

    def __init__(self, name: str = "workflow") -> None:
        super().__init__(name)

    def add_step(self, step_id: str, label: str = "", step_type: str = "task") -> None:
        self.add_node(step_id, label, kind=step_type)

    def add_transition(self, source: str, target: str, condition: str | None = None) -> None:
        attrs = {"condition": condition} if condition else {}
        self.add_edge(source, target, kind="transition", **attrs)


class DatabaseGraph(GraphBuilder):
    """Graph of database tables and relations."""

    def __init__(self, name: str = "database") -> None:
        super().__init__(name)

    def add_table(self, table_id: str, label: str = "", columns: list[str] | None = None) -> None:
        self.add_node(table_id, label, kind="table", columns=columns or [])

    def add_relation(self, source: str, target: str, kind: str = "foreign_key") -> None:
        self.add_edge(source, target, kind=kind)


class AgentNetwork(GraphBuilder):
    """Graph of agent relationships and communication flows."""

    def __init__(self, name: str = "agents") -> None:
        super().__init__(name)

    def add_agent(self, agent_id: str, label: str = "", status: str = "idle") -> None:
        self.add_node(agent_id, label, kind="agent", status=status)

    def add_message(self, source: str, target: str) -> None:
        self.add_edge(source, target, kind="message")
