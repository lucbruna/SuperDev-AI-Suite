"""Coupling analyzer: afferent/efferent coupling per package.

Classic package metrics (Martin's metrics, adapted):
* Afferent coupling (Ca): number of packages that depend on this one.
* Efferent coupling (Ce): number of packages this one depends on.
* Instability I = Ce / (Ca + Ce); I close to 1 means unstable/fragile.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def _package_of(node_id: str) -> str:
    return node_id.split(":", 1)[1].split("/", 1)[0] if ":" in node_id else node_id


def coupling_metrics(graph: ArchitectureGraph) -> dict[str, Any]:
    packages: dict[str, dict[str, Any]] = {}
    for node in graph.nodes():
        if node.kind not in {"file", "package", "module"}:
            continue
        pkg = _package_of(node.id)
        bucket = packages.setdefault(pkg, {"ca": set(), "ce": set()})
        for incoming in graph.incoming(node.id):
            bucket["ca"].add(_package_of(incoming))
        for outgoing in graph.outgoing(node.id):
            bucket["ce"].add(_package_of(outgoing))

    results: list[dict[str, Any]] = []
    for pkg, bucket in packages.items():
        ca = len(bucket["ca"])
        ce = len(bucket["ce"])
        instability = round(ce / (ca + ce), 3) if (ca + ce) else 0.0
        abstractness = 0.0
        results.append(
            {
                "package": pkg,
                "afferent": ca,
                "efferent": ce,
                "instability": instability,
                "abstractness": abstractness,
                "balanced": abs(instability - abstractness) < 0.5,
            }
        )
    results.sort(key=lambda r: r["instability"], reverse=True)
    return {"packages": results, "total": len(results)}


def hot_couples(graph: ArchitectureGraph, top: int = 10) -> list[dict[str, Any]]:
    """Most connected package pairs (highest cross-package edge counts)."""
    pair_count: dict[tuple[str, str], int] = {}
    for node in graph.nodes():
        pkg = _package_of(node.id)
        for outgoing in graph.outgoing(node.id):
            other = _package_of(outgoing)
            if pkg == other:
                continue
            key = (pkg, other)
            pair_count[key] = pair_count.get(key, 0) + 1
    ranked = sorted(pair_count.items(), key=lambda kv: kv[1], reverse=True)[:top]
    return [
        {"source": a, "target": b, "edges": count} for (a, b), count in ranked
    ]
