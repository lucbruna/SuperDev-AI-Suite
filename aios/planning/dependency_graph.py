"""DependencyGraph: DAG of tasks with topological order, cycle detection and critical path."""
from __future__ import annotations

from typing import Any


class DependencyGraph:
    """Deterministic directed acyclic graph of task dependencies.

    ``add_edge(task_id, depends_on)`` records that ``task_id`` cannot start
    until ``depends_on`` completes. Edges point from the dependent to its
    dependency.
    """

    def __init__(self) -> None:
        self._nodes: dict[str, dict[str, Any]] = {}
        self._dependencies: dict[str, list[str]] = {}
        self._dependents: dict[str, list[str]] = {}

    def add_node(self, node_id: str, **data: Any) -> None:
        if node_id not in self._nodes:
            self._nodes[node_id] = {}
            self._dependencies[node_id] = []
            self._dependents[node_id] = []
        self._nodes[node_id].update(data)

    def add_edge(self, node_id: str, depends_on: str) -> None:
        if node_id not in self._nodes:
            self.add_node(node_id)
        if depends_on not in self._nodes:
            self.add_node(depends_on)
        if depends_on not in self._dependencies[node_id]:
            self._dependencies[node_id].append(depends_on)
        if node_id not in self._dependents[depends_on]:
            self._dependents[depends_on].append(node_id)

    def nodes(self) -> list[str]:
        return sorted(self._nodes)

    def dependencies_of(self, node_id: str) -> list[str]:
        return list(self._dependencies.get(node_id, []))

    def dependents_of(self, node_id: str) -> list[str]:
        return list(self._dependents.get(node_id, []))

    def roots(self) -> list[str]:
        return sorted(n for n in self._nodes if not self._dependencies[n])

    def leaves(self) -> list[str]:
        return sorted(n for n in self._nodes if not self._dependents[n])

    def has_cycle(self) -> bool:
        return self._cycle_node() is not None

    def _cycle_node(self) -> str | None:
        """Kahn's algorithm: any node left with in-degree > 0 is on a cycle."""
        in_degree = {n: len(self._dependencies[n]) for n in self._nodes}
        ready = sorted(n for n, d in in_degree.items() if d == 0)
        consumed = 0
        while ready:
            node = ready.pop(0)
            consumed += 1
            for dep in self._dependents[node]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    ready.append(dep)
                    ready.sort()
        for node in self._nodes:
            if in_degree[node] > 0:
                return node
        return None

    def topological_sort(self) -> list[str]:
        node = self._cycle_node()
        if node is not None:
            raise ValueError(f"dependency cycle detected involving {node!r}")
        in_degree = {n: len(self._dependencies[n]) for n in self._nodes}
        ready = sorted(n for n, d in in_degree.items() if d == 0)
        order: list[str] = []
        while ready:
            current = ready.pop(0)
            order.append(current)
            for dep in self._dependents[current]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    ready.append(dep)
                    ready.sort()
        return order

    def level_of(self, node_id: str) -> int:
        """Longest distance from a root node (roots are level 0)."""
        memo: dict[str, int] = {}

        def _level(n: str) -> int:
            if n in memo:
                return memo[n]
            deps = self._dependencies[n]
            memo[n] = 0 if not deps else 1 + max(_level(d) for d in deps)
            return memo[n]

        return _level(node_id)

    def duration_of(self, node_id: str, default: float = 1.0) -> float:
        return float(self._nodes.get(node_id, {}).get("duration", default))

    def critical_path(self) -> tuple[list[str], float]:
        """Longest path through the graph by duration, with deterministic tie-breaks."""
        order = self.topological_sort()
        if not order:
            return [], 0.0
        total: dict[str, float] = {}
        pred: dict[str, str | None] = {}
        for n in order:
            deps = self._dependencies[n]
            if not deps:
                total[n] = self.duration_of(n)
                pred[n] = None
            else:
                best_dep = max(deps, key=lambda d: (total[d], d))
                total[n] = total[best_dep] + self.duration_of(n)
                pred[n] = best_dep
        end = max(order, key=lambda n: (total[n], n))
        path: list[str] = []
        current: str | None = end
        while current is not None:
            path.append(current)
            current = pred[current]
        path.reverse()
        return path, total[end]
