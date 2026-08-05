"""Trust graph: trust boundaries between architecture layers and entities.

Assigns a trust level to each node based on its layer (infrastructure =
highest privilege, frontend = lowest) and flags edges that cross trust
boundaries — the classic attack-surface view of the architecture.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph

# Higher number = more privileged (more trusted).
_TRUST_BY_LAYER = {
    "infrastructure": 5,
    "core": 4,
    "ai": 4,
    "workflow_engine": 3,
    "runtime_engine": 3,
    "modules": 3,
    "backend": 3,
    "cli": 2,
    "frontend": 1,
    "external": 0,
}

_EDGE_TRUST_KINDS = {"imports", "uses", "calls", "depends_on", "consumes"}


class TrustGraph:
    """Trust-boundary analysis over the architecture graph."""

    def analyze(self, graph: ArchitectureGraph) -> dict[str, Any]:
        boundary_crossings: list[dict[str, Any]] = []
        for edge in graph.edges():
            if edge.kind not in _EDGE_TRUST_KINDS:
                continue
            source = graph.get_node(edge.source)
            target = graph.get_node(edge.target)
            if source is None or target is None:
                continue
            src_trust = _TRUST_BY_LAYER.get(source.layer, 1)
            dst_trust = _TRUST_BY_LAYER.get(target.layer, 1)
            if src_trust > dst_trust:
                boundary_crossings.append(
                    {
                        "source": edge.source,
                        "source_layer": source.layer,
                        "target": edge.target,
                        "target_layer": target.layer,
                        "kind": edge.kind,
                        "direction": "privileged -> less privileged",
                    }
                )
        return {
            "total_crossings": len(boundary_crossings),
            "layers": {layer: level for layer, level in sorted(_TRUST_BY_LAYER.items(), key=lambda kv: -kv[1])},
            "crossings": boundary_crossings[:200],
        }

    def module_trust(self, graph: ArchitectureGraph) -> list[dict[str, Any]]:
        """Trust level per module/package node."""
        rows: list[dict[str, Any]] = []
        for node in graph.nodes():
            if node.kind not in {"module", "package"}:
                continue
            rows.append(
                {
                    "id": node.id,
                    "name": node.name,
                    "layer": node.layer or "?",
                    "trust": _TRUST_BY_LAYER.get(node.layer, 1),
                }
            )
        rows.sort(key=lambda r: (-r["trust"], r["id"]))
        return rows


def trust_analysis(graph: ArchitectureGraph) -> dict[str, Any]:
    """One-shot convenience helper."""
    return TrustGraph().analyze(graph)
