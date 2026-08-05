"""Natural-language explanations for graph entities and relationships.

Explains *why* a node matters, *what* it depends on, *who* depends on it and
*what happens* if it changes. Produces deterministic, template-driven text —
no LLM required — with an optional hook to hand the context to an external
model for free-form prose.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.core.impact_engine import (
    dependents,
    dependencies,
    risk_score,
)
from modules.architecture_graph.core.navigation_engine import path_between
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph

_KIND_LABELS = {
    "file": "file",
    "module": "module",
    "package": "package",
    "api": "API endpoint",
    "agent": "agent",
    "plugin": "plugin",
    "workflow": "workflow",
    "service": "service",
    "database": "database",
    "external": "external dependency",
    "config": "configuration file",
    "document": "document",
}


class ArchitectureExplainer:
    """Template-based explanations over the graph."""

    def explain_node(self, graph: ArchitectureGraph, node_id: str) -> dict[str, Any]:
        node = graph.get_node(node_id)
        if node is None:
            return {"found": False, "text": f"No node found for '{node_id}'."}

        label = _KIND_LABELS.get(node.kind, node.kind)
        in_ids = graph.incoming(node.id)
        out_ids = graph.outgoing(node.id)
        parts = [
            f"{node.name} is a {label}",
            f"in layer '{node.layer or 'unassigned'}'",
            f"at {node.path or node.id}.",
        ]
        if in_ids:
            parts.append(f"{len(in_ids)} other nodes depend on it")
            parts.append(f"({', '.join(in_ids[:5])}{'...' if len(in_ids) > 5 else ''}).")
        else:
            parts.append("No other node depends on it.")
        if out_ids:
            parts.append(f"It depends on {len(out_ids)} node(s)")
            parts.append(f"({', '.join(out_ids[:5])}{'...' if len(out_ids) > 5 else ''}).")
        else:
            parts.append("It has no outgoing dependencies.")

        risk = risk_score(graph, node.id)
        parts.append(
            f"Its change risk is {risk.get('reason', 'unknown')} "
            f"({risk.get('risk', 0.0):.2f})."
        )
        return {
            "found": True,
            "node_id": node_id,
            "text": " ".join(parts),
            "risk": risk,
        }

    def explain_edge(self, graph: ArchitectureGraph, source: str, target: str) -> dict[str, Any]:
        src = graph.get_node(source)
        dst = graph.get_node(target)
        if src is None or dst is None:
            return {
                "found": False,
                "text": f"Edge {source} -> {target}: one endpoint is missing.",
            }
        edges = graph.edges_between(source, target)
        kinds = sorted({e.kind for e in edges}) or ["(no direct edge)"]
        text = (
            f"{src.name} ({src.kind}) has a direct '{' + '.join(kinds)}' relationship "
            f"with {dst.name} ({dst.kind}) in layer {dst.layer or 'unassigned'}."
        )
        return {"found": True, "text": text, "kinds": kinds, "edges": [e.to_dict() for e in edges]}

    def explain_path(
        self, graph: ArchitectureGraph, source: str, target: str
    ) -> dict[str, Any]:
        path = path_between(graph, source, target)
        if not path:
            return {
                "found": False,
                "text": f"No path from {source} to {target}.",
            }
        names = []
        for node_id in path:
            node = graph.get_node(node_id)
            names.append(node.name if node else node_id)
        return {
            "found": True,
            "path": path,
            "text": " -> ".join(names),
            "hops": len(path) - 1,
        }

    def explain_impact(self, graph: ArchitectureGraph, node_id: str) -> dict[str, Any]:
        node = graph.get_node(node_id)
        if node is None:
            return {"found": False, "text": f"Unknown node '{node_id}'."}
        affected = dependents(graph, node_id)
        affected_ids = [d["id"] for d in affected.get("dependencies", [])]
        consumed = dependencies(graph, node_id)
        text = (
            f"Changing {node.name} could impact {affected.get('total', 0)} node(s) "
            f"transitively; it consumes {consumed.get('total', 0)} node(s). "
            f"Top affected: {', '.join(affected_ids[:5]) or 'none'}."
        )
        return {
            "found": True,
            "text": text,
            "affected_count": affected.get("total", 0),
            "affected": affected_ids,
        }

    def explain_all(
        self, graph: ArchitectureGraph, node_id: str
    ) -> dict[str, Any]:
        """Consolidated explanation for a node (identity + impact + paths)."""
        base = self.explain_node(graph, node_id)
        if not base.get("found"):
            return base
        impact = self.explain_impact(graph, node_id)
        node = graph.get_node(node_id)
        neighbors = graph.neighbors(node_id)
        return {
            "found": True,
            "node_id": node_id,
            "summary": base["text"],
            "impact": impact,
            "neighbors": neighbors[:20],
            "risk": base["risk"],
            "kind": node.kind if node else "",
            "layer": node.layer if node else "",
        }


def explain(graph: ArchitectureGraph, node_id: str) -> dict[str, Any]:
    """One-shot convenience helper."""
    return ArchitectureExplainer().explain_all(graph, node_id)
