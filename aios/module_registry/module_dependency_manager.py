"""ModuleDependencyManager: dependency graph with deterministic resolution order."""
from __future__ import annotations

from typing import Any


class ModuleDependencyManager:
    """Tracks which module names each module depends on."""

    def __init__(self) -> None:
        self._graph: dict[str, list[str]] = {}

    def add_module(self, module_name: str, dependencies: list[str]) -> None:
        self._graph[module_name] = list(dependencies)

    def remove_module(self, module_name: str) -> bool:
        return self._graph.pop(module_name, None) is not None

    def requires(self, module_name: str) -> list[str]:
        return list(self._graph.get(module_name, []))

    def dependents(self, module_name: str) -> list[str]:
        return sorted(
            name for name, deps in self._graph.items() if module_name in deps
        )

    def names(self) -> list[str]:
        return sorted(self._graph)

    def resolve_order(self, module_names: list[str]) -> list[str]:
        """Deterministic topological order; raises ValueError on a cycle."""
        subset = set(module_names)
        in_degree = {name: 0 for name in subset}
        edges: dict[str, list[str]] = {name: [] for name in subset}
        for name in subset:
            for dep in self._graph.get(name, []):
                if dep in subset:
                    edges[dep].append(name)
                    in_degree[name] += 1
        ready = sorted(name for name, degree in in_degree.items() if degree == 0)
        order: list[str] = []
        while ready:
            current = ready.pop(0)
            order.append(current)
            for dependent in edges[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    ready.append(dependent)
                    ready.sort()
        if len(order) != len(subset):
            leftover = sorted(name for name in subset if name not in order)
            raise ValueError(f"dependency cycle detected involving {leftover}")
        return order

    def snapshot(self) -> dict[str, Any]:
        return {name: list(deps) for name, deps in sorted(self._graph.items())}
