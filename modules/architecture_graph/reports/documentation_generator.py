"""Documentation generator: markdown docs derived from the graph.

Produces a structured ``ARCHITECTURE.md``-style document describing modules,
APIs, agents, plugins, workflows, databases and their dependency relations —
kept in sync with the actual codebase.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.analytics.module_score import module_scores
from modules.architecture_graph.core.metrics_engine import graph_metrics
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


class DocumentationGenerator:
    """Generate human-readable architecture documentation from a graph."""

    def generate(self, graph: ArchitectureGraph) -> str:
        sections = [
            f"# Architecture Documentation — {graph.name}",
            "",
            f"> Generated from `{graph.project_root or 'project root'}` — build at {graph.built_at}",
            "",
            "## Overview",
            "",
            self._overview(graph),
            "",
            "## Modules",
            "",
            self._modules(graph),
            "",
            "## APIs",
            "",
            self._apis(graph),
            "",
            "## Agents & Plugins & Workflows",
            "",
            self._platform_entities(graph),
            "",
            "## Dependencies",
            "",
            self._dependencies(graph),
            "",
        ]
        return "\n".join(sections)

    def _overview(self, graph: ArchitectureGraph) -> str:
        metrics = graph_metrics(graph)
        stats = graph.stats()
        kinds = ", ".join(f"{k}: {v}" for k, v in sorted(stats.get("kinds", {}).items()))
        return (
            f"- **Nodes:** {metrics.get('nodes', 0)} "
            f"(kinds — {kinds})\n"
            f"- **Edges:** {metrics.get('edges', 0)}\n"
            f"- **Layers:** {', '.join(sorted(stats.get('layers', {})))}"
        )

    def _modules(self, graph: ArchitectureGraph) -> str:
        scores = {s["id"]: s for s in module_scores(graph)}
        modules = [
            n for n in graph.nodes()
            if n.kind == "module" or (n.kind == "package" and n.path.endswith("/"))
        ]
        if not modules:
            return "_No modules detected._"
        lines = ["| Module | Layer | Score | Files |", "| --- | --- | --- | --- |"]
        for node in sorted(modules, key=lambda n: n.id):
            score = scores.get(node.id, {})
            lines.append(
                f"| {node.name} | {node.layer or '?'} | "
                f"{score.get('score', '-')} | {score.get('size', '-')} |"
            )
        return "\n".join(lines)

    def _apis(self, graph: ArchitectureGraph) -> str:
        apis = [n for n in graph.nodes() if n.kind == "api"]
        if not apis:
            return "_No API endpoints detected._"
        lines = ["| Endpoint | Method | File |", "| --- | --- | --- |"]
        for node in sorted(apis, key=lambda n: (n.name, n.meta.get("method", ""))):
            lines.append(
                f"| {node.name} | {node.meta.get('method', '?')} | {node.path or node.id} |"
            )
        return "\n".join(lines)

    def _platform_entities(self, graph: ArchitectureGraph) -> str:
        lines: list[str] = []
        for kind in ("agent", "plugin", "workflow", "service", "database"):
            nodes = [n for n in graph.nodes() if n.kind == kind]
            if not nodes:
                continue
            lines.append(f"### {kind.capitalize()}s")
            lines.append("")
            lines.append("\n".join(f"- `{n.name}` ({n.path or n.id})" for n in sorted(nodes, key=lambda n: n.id)))
            lines.append("")
        return "\n".join(lines) if lines else "_No platform entities detected._"

    def _dependencies(self, graph: ArchitectureGraph) -> str:
        lines = ["### Top modules by dependents", ""]
        ranked = sorted(
            (
                (node, len(graph.incoming(node.id)))
                for node in graph.nodes()
                if node.kind in {"module", "package"}
            ),
            key=lambda item: item[1],
            reverse=True,
        )[:10]
        if ranked:
            lines.append("\n".join(f"- `{n.id}` — {count} dependents" for n, count in ranked))
        else:
            lines.append("_No module-level dependents computed._")
        return "\n".join(lines)

    def write(self, graph: ArchitectureGraph, path: str) -> dict[str, Any]:
        """Write the generated docs to disk."""
        from pathlib import Path

        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self.generate(graph), encoding="utf-8")
        return {"path": str(dest), "bytes": dest.stat().st_size}


def generate_documentation(graph: ArchitectureGraph) -> str:
    """One-shot convenience helper."""
    return DocumentationGenerator().generate(graph)
