"""Access graph: who can access what, derived from permission mappings.

Builds a compact access model (permission source -> API endpoint -> owning
module) so security exposure is visible per module in the architecture graph.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.edge_builder import exposes
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.mappers.permission_mapper import PermissionMapper


class AccessGraph:
    """Access-oriented view over permission definitions."""

    def __init__(self, root: str) -> None:
        self.root = root
        self.mapper = PermissionMapper(root)

    def build(self, graph: ArchitectureGraph | None = None) -> dict[str, Any]:
        """Compute access relations. Optionally wire them onto a graph."""
        if not self.mapper.records:
            self.mapper.discover()
        access: list[dict[str, Any]] = []
        for record in self.mapper.records:
            rel = record.get("path", "")
            owner_module = rel.split("/")[1] if len(rel.split("/")) > 1 else rel
            for capability in record.get("capabilities", []):
                access.append(
                    {
                        "capability": capability,
                        "source": rel,
                        "owner_module": owner_module,
                        "guard_file": rel,
                    }
                )
        if graph is not None:
            self._wire(graph)
        return {
            "total": len(access),
            "capabilities": sorted({a["capability"] for a in access}),
            "modules": sorted({a["owner_module"] for a in access}),
            "access": access[:500],
        }

    def _wire(self, graph: ArchitectureGraph) -> int:
        """Add exposes edges from permission configs to their API nodes."""
        edges = 0
        for record in self.mapper.records:
            rel = record.get("path", "")
            node_id = f"config:{rel}"
            if not graph.has_node(node_id):
                continue
            if "/api/" in rel:
                route = rel.split("/api/", 1)[1].rsplit(".py", 1)[0].replace("/", ":")
                if graph.has_node(f"api:{route}") and graph.add_edge(exposes(node_id, f"api:{route}")):
                    edges += 1
        return edges

    def module_exposure(self) -> list[dict[str, Any]]:
        """Capability count per module (attack-surface ranking)."""
        report = self.build()
        counts: dict[str, int] = {}
        for item in report.get("access", []):
            module = item["owner_module"]
            counts[module] = counts.get(module, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
        return [{"module": m, "capabilities": c} for m, c in ranked]


def build_access_graph(root: str) -> dict[str, Any]:
    """One-shot convenience helper."""
    return AccessGraph(root).build()
