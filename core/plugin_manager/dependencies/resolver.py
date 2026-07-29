from __future__ import annotations

from typing import Any


class CircularDependencyError(Exception):
    pass


class MissingDependencyError(Exception):
    pass


class DependencyResolver:
    def resolve(
        self,
        manifest: dict[str, Any],
        available_plugins: dict[str, dict[str, Any]],
    ) -> list[str]:
        dependencies = manifest.get("dependencies", [])
        dep_names = []
        for dep in dependencies:
            if isinstance(dep, str):
                dep_names.append(dep)
            elif isinstance(dep, dict):
                dep_names.append(dep.get("name", ""))

        graph: dict[str, list[str]] = {}
        graph["__root__"] = dep_names

        for dep_name in dep_names:
            if dep_name in available_plugins:
                dep_manifest = available_plugins[dep_name].get("manifest", {})
                sub_deps = []
                for sub in dep_manifest.get("dependencies", []):
                    if isinstance(sub, str):
                        sub_deps.append(sub)
                    elif isinstance(sub, dict):
                        sub_deps.append(sub.get("name", ""))
                graph[dep_name] = sub_deps
            else:
                raise MissingDependencyError(f"Dependency '{dep_name}' not found in available plugins")

        self._detect_circular(graph)

        resolved = self._topological_sort(graph, "__root__")
        resolved = [d for d in resolved if d != "__root__"]
        return resolved

    def _detect_circular(self, graph: dict[str, list[str]]) -> None:
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {node: WHITE for node in graph}

        def dfs(node: str) -> None:
            color[node] = GRAY
            for neighbor in graph.get(node, []):
                if neighbor not in color:
                    color[neighbor] = WHITE
                if color[neighbor] == GRAY:
                    raise CircularDependencyError(f"Circular dependency detected involving '{node}' and '{neighbor}'")
                if color[neighbor] == WHITE:
                    dfs(neighbor)
            color[node] = BLACK

        for node in graph:
            if color[node] == WHITE:
                dfs(node)

    def _topological_sort(self, graph: dict[str, list[str]], start: str) -> list[str]:
        visited: set[str] = set()
        result: list[str] = []

        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for neighbor in graph.get(node, []):
                if neighbor in graph:
                    dfs(neighbor)
            result.append(node)

        dfs(start)

        for node in graph:
            if node not in visited:
                dfs(node)

        return result