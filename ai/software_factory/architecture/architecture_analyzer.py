"""Analyzer for architecture metrics and quality."""

from collections import Counter
from typing import Any

from .models import ArchitectureComponent, Connector


class ArchitectureAnalyzer:
    """Analyzes architecture for metrics, complexity, and quality."""

    def analyze(self, components: list[ArchitectureComponent], connectors: list[Connector]) -> dict[str, Any]:
        if not components:
            return {"empty": True}

        type_dist = Counter(c.component_type.value for c in components)
        conn_type_dist = Counter(c.connector_type.value for c in connectors)
        dep_counts = [len(c.dependencies) for c in components]
        avg_deps = sum(dep_counts) / len(dep_counts) if dep_counts else 0

        interface_counts = [len(c.interfaces) for c in components]
        avg_interfaces = sum(interface_counts) / len(interface_counts) if interface_counts else 0

        return {
            "total_components": len(components),
            "total_connectors": len(connectors),
            "component_type_distribution": dict(type_dist),
            "connector_type_distribution": dict(conn_type_dist),
            "avg_dependencies": avg_deps,
            "avg_interfaces": avg_interfaces,
            "max_dependencies": max(dep_counts) if dep_counts else 0,
            "coupling_score": avg_deps / 5.0,
            "cohesion_score": avg_interfaces / 3.0,
        }

    def compute_complexity(
        self, components: list[ArchitectureComponent], connectors: list[Connector]
    ) -> dict[str, Any]:
        nodes = len(components)
        edges = len(connectors)
        density = (2 * edges) / (nodes * (nodes - 1)) if nodes > 1 else 0
        return {
            "nodes": nodes,
            "edges": edges,
            "density": density,
            "complexity_rating": "high" if density > 0.5 else "medium" if density > 0.2 else "low",
        }

    def find_circular_deps(self, components: list[ArchitectureComponent]) -> list[list[str]]:
        """Find potential circular dependencies."""
        adj: dict[str, list[str]] = {c.component_id: list(c.dependencies) for c in components}
        cycles: list[list[str]] = []
        visited = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return
            path.append(node)
            for neighbor in adj.get(node, []):
                if neighbor in adj:
                    dfs(neighbor)
            path.pop()
            visited.add(node)

        for comp in components:
            dfs(comp.component_id)
        return cycles

    def get_quality_assessment(
        self, components: list[ArchitectureComponent], connectors: list[Connector]
    ) -> dict[str, Any]:
        analysis = self.analyze(components, connectors)
        complexity = self.compute_complexity(components, connectors)
        cycles = self.find_circular_deps(components)

        issues = []
        if analysis["avg_dependencies"] > 5:
            issues.append("High coupling detected")
        if complexity["density"] > 0.7:
            issues.append("Very dense architecture")
        if cycles:
            issues.append(f"Circular dependencies found: {len(cycles)}")

        return {
            "analysis": analysis,
            "complexity": complexity,
            "circular_deps": len(cycles),
            "issues": issues,
            "overall_quality": "good" if not issues else "needs_improvement",
        }
