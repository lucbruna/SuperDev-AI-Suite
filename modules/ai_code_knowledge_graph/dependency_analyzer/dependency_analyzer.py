"""Dependency analyzer — per-file dependency report + analyzer hook.

Combines the relation builder (derived depends_on/references edges) with the
dependency resolver (closures, impact sets, cycles) into a single report.
Registered as an ``analyzer`` so the pipeline index stage runs it and stores
``dependency_analysis`` on the context.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.dependency_analyzer.resolver import DependencyResolver
from modules.ai_code_knowledge_graph.relations.builder import RelationBuilder


class DependencyAnalyzer:
    """File-level dependency analysis over the knowledge graph."""

    def __init__(self) -> None:
        self.relations = RelationBuilder()

    # ── Analyzer interface (invoked by the pipeline index stage) ──────────
    def index(self, ctx) -> dict[str, Any]:
        """Analyzer hook: analyze the graph and store the report on the context."""
        if not getattr(ctx.config, "run_relations", True):
            ctx.record("relations_skipped", True)
            return {"files": 0, "cycles": 0, "detail": "relations disabled"}
        graph = ctx.memory.get("knowledge_graph")
        if not graph:
            return {"files": 0, "cycles": 0, "detail": "no graph"}
        analysis = self.analyze(graph)
        ctx.memory.put("dependency_analysis", analysis)
        ctx.record("dependency_files", analysis["stats"]["files_with_deps"])
        ctx.record("dependency_edges", analysis["stats"]["derived_edges"])
        return {
            "files": analysis["stats"]["files_with_deps"],
            "cycles": len(analysis["cycles"]),
        }

    # ── Analysis ──────────────────────────────────────────────────────────
    def analyze(self, graph: dict[str, Any]) -> dict[str, Any]:
        """Return a per-file dependency report for a knowledge graph."""
        derived = self.relations.build(graph)
        resolver = DependencyResolver(graph)
        by_file: dict[str, Any] = {}
        for node in graph.get("nodes", []):
            if node.get("kind") != "file":
                continue
            file_id = node["id"]
            by_file[file_id] = {
                "dependencies": resolver.dependencies(file_id),
                "impact": resolver.impact(file_id),
            }
        return {
            "project_root": graph.get("project_root", ""),
            "by_file": by_file,
            "cycles": resolver.find_cycles(),
            "derived_edges": derived["edges"],
            "stats": {
                "files": len(by_file),
                "files_with_deps": sum(1 for entry in by_file.values() if entry["dependencies"]),
                "derived_edges": len(derived["edges"]),
                "cycles": len(resolver.find_cycles()),
            },
        }
