from __future__ import annotations

from typing import Any


class DependencyAnalyzer:
    """Analyzes dependencies between components with cycle detection."""

    def __init__(self) -> None:
        self._dependencies: dict[str, list[str]] = {}

    def add_dependency(self, component: str, depends_on: str) -> None:
        if component not in self._dependencies:
            self._dependencies[component] = []
        if depends_on not in self._dependencies[component]:
            self._dependencies[component].append(depends_on)
        if depends_on not in self._dependencies:
            self._dependencies[depends_on] = []

    def remove_dependency(self, component: str, depends_on: str) -> bool:
        if component in self._dependencies and depends_on in self._dependencies[component]:
            self._dependencies[component].remove(depends_on)
            return True
        return False

    def get_dependencies(self, component: str) -> list[str]:
        return list(self._dependencies.get(component, []))

    def get_dependents(self, component: str) -> list[str]:
        return [c for c, deps in self._dependencies.items() if component in deps]

    def detect_cycles(self) -> list[list[str]]:
        cycles: list[list[str]] = []
        visited: set[str] = set()
        path: list[str] = []
        path_set: set[str] = set()

        def dfs(node: str) -> None:
            if node in path_set:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            if node in visited:
                return
            visited.add(node)
            path.append(node)
            path_set.add(node)
            for neighbor in self._dependencies.get(node, []):
                dfs(neighbor)
            path.pop()
            path_set.discard(node)

        for component in list(self._dependencies.keys()):
            if component not in visited:
                dfs(component)

        return cycles

    @property
    def component_count(self) -> int:
        return len(self._dependencies)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dependencies": self._dependencies,
            "component_count": self.component_count,
        }
