"""Resolver for version dependency graphs."""
from typing import List, Dict, Any, Optional
from .models import DependencyGraph, VersionConstraint


class DependencyResolver:
    def __init__(self):
        self._graphs: Dict[str, DependencyGraph] = {}
        self._constraints: List[VersionConstraint] = []

    def create_graph(self, name: str) -> DependencyGraph:
        graph = DependencyGraph()
        self._graphs[name] = graph
        return graph

    def get_graph(self, name: str) -> Optional[DependencyGraph]:
        return self._graphs.get(name)

    def add_constraint(self, constraint: VersionConstraint) -> None:
        self._constraints.append(constraint)

    def resolve(self, graph_name: str) -> List[str]:
        graph = self._graphs.get(graph_name)
        if not graph:
            return []
        visited = set()
        result: List[str] = []

        def dfs(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in graph.get_dependencies(node):
                dfs(dep)
            result.append(node)

        for node in graph.nodes:
            dfs(node)
        return result

    def check_compatibility(self, versions: Dict[str, str]) -> List[str]:
        issues = []
        for constraint in self._constraints:
            ver = versions.get(constraint.name, "")
            if ver and not constraint.satisfies(ver):
                issues.append(f"{constraint.name}={ver} does not satisfy constraint")
        return issues
