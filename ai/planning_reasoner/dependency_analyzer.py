from __future__ import annotations

from typing import Any


class DependencyAnalyzer:
    """Analyzes dependencies between tasks and resources."""

    def __init__(self) -> None:
        self._dependencies: dict[str, list[str]] = {}

    def add_dependency(self, task: str, depends_on: str) -> None:
        if task not in self._dependencies:
            self._dependencies[task] = []
        self._dependencies[task].append(depends_on)

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        tasks = context.get("tasks", [])
        graph: dict[str, list[str]] = {}
        for task in tasks:
            task_id = task.get("id", "")
            deps = self._dependencies.get(task_id, [])
            graph[task_id] = deps
        return {
            "dependency_graph": graph,
            "critical_path": await self._find_critical_path(graph),
            "parallel_groups": await self._find_parallel_groups(graph),
        }

    async def _find_critical_path(self, graph: dict[str, list[str]]) -> list[str]:
        visited: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in graph.get(node, []):
                dfs(dep)
            path.append(node)

        for node in graph:
            dfs(node)
        return path

    async def _find_parallel_groups(self, graph: dict[str, list[str]]) -> list[list[str]]:
        groups: list[list[str]] = []
        assigned: set[str] = set()
        for node, deps in graph.items():
            if not deps and node not in assigned:
                groups.append([node])
                assigned.add(node)
        remaining = [n for n in graph if n not in assigned]
        if remaining:
            groups.append(remaining)
        return groups
