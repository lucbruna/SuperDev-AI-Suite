"""Module score: how central/healthy each platform module is (0..100)."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def module_scores(graph: ArchitectureGraph) -> list[dict[str, Any]]:
    """Score every module node (and top-level package) from 0 to 100."""
    modules: dict[str, dict[str, Any]] = {}
    for node in graph.nodes():
        if node.kind not in {"module", "package"}:
            continue
        key = node.id
        bucket = modules.setdefault(
            key,
            {
                "id": key,
                "name": node.name,
                "kind": node.kind,
                "path": node.path,
                "files": 0,
                "fan_in": 0,
                "fan_out": 0,
                "api_count": 0,
                "size": 0,
            },
        )
        bucket["size"] += node.size

    for node in graph.nodes():
        if node.kind == "file":
            parts = (node.path or node.name).split("/")
            if not parts:
                continue
            if parts[0] == "modules" and len(parts) >= 2:
                key = f"module:{parts[1]}"
            else:
                key = f"package:{parts[0]}"
            bucket = modules.get(key)
            if bucket is None:
                continue
            bucket["files"] += 1
            bucket["fan_in"] += len(graph.incoming(node.id))
            bucket["fan_out"] += len(graph.outgoing(node.id))
        elif node.kind == "api":
            parts = (node.path or node.name).split("/")
            if not parts:
                continue
            key = f"package:{parts[0]}"
            bucket = modules.get(key)
            if bucket is not None:
                bucket["api_count"] += 1

    results: list[dict[str, Any]] = []
    for bucket in modules.values():
        importance = min(bucket["fan_in"] / 40.0, 1.0)
        size_score = min(bucket["files"] / 60.0, 1.0)
        api_score = min(bucket["api_count"] / 15.0, 1.0)
        coupling_penalty = min(bucket["fan_out"] / 120.0, 1.0) * 0.5
        score = round(
            max(0.0, 100.0 * (0.45 * importance + 0.25 * size_score + 0.15 * api_score - coupling_penalty)),
            1,
        )
        bucket["score"] = score
        bucket["tier"] = (
            "core" if score >= 70 else "active" if score >= 40 else "auxiliary"
        )
        results.append(bucket)

    results.sort(key=lambda m: m["score"], reverse=True)
    return results
