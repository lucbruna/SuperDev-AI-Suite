"""Dependency manager — declares service dependencies, detects cycles, topo order."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.integration.module_registry import get_registry


class DependencyError(Exception):
    """Raised when the dependency graph is cyclic or references unknown services."""


class DependencyManager:
    """Tracks declared dependencies between registered services."""

    def __init__(self, registry=None) -> None:  # type: ignore[no-untyped-def]
        self._registry = registry or get_registry()
        self._deps: dict[str, set[str]] = {}

    def declare(self, service: str, depends_on: str | list[str]) -> None:
        """Declare that ``service`` depends on one or more other services."""
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        for dep in depends_on:
            if dep == service:
                raise DependencyError(f"Service '{service}' cannot depend on itself")
        self._deps.setdefault(service, set()).update(depends_on)

    def dependencies(self, name: str) -> list[str]:
        return sorted(self._deps.get(name, ()))

    def dependents(self, name: str) -> list[str]:
        return sorted(s for s, deps in self._deps.items() if name in deps)

    def is_satisfied(self, name: str) -> bool:
        """All declared dependencies are registered (and have their own deps satisfied)."""
        if name not in self._registry._services and name not in self._deps:  # noqa: SLF001
            return False
        return all(
            self._registry.has(dep) and self.is_satisfied(dep)
            for dep in self._deps.get(name, ())
        )

    def validate(self) -> None:
        """Raise DependencyError if the graph is cyclic or a dependency is missing."""
        self._check_cycle()
        for service in self._deps:
            for dep in self._deps[service]:
                if not self._registry.has(dep):
                    raise DependencyError(
                        f"Service '{service}' depends on unregistered '{dep}'"
                    )

    def resolution_order(self) -> list[str]:
        """Kahn topological sort: dependencies before dependents."""
        self.validate()
        import collections

        deps = {s: set(d) for s, d in self._deps.items()}
        for s in self._registry._services:  # noqa: SLF001
            deps.setdefault(s, set())
        ready = collections.deque(sorted(s for s, d in deps.items() if not d))
        order: list[str] = []
        while ready:
            node = ready.popleft()
            order.append(node)
            for s in sorted(deps):
                if node in deps[s]:
                    deps[s].discard(node)
                    if not deps[s] and s not in order:
                        ready.append(s)
        return order

    def snapshot(self) -> dict[str, Any]:
        return {
            "declared": sorted(self._deps),
            "edges": [
                {"service": s, "depends_on": self.dependencies(s)}
                for s in sorted(self._deps)
            ],
            "order": self.resolution_order(),
            "satisfied": {s: self.is_satisfied(s) for s in sorted(self._deps)},
        }

    def _check_cycle(self) -> None:
        white, gray, black = 0, 1, 2
        color: dict[str, int] = {}

        def visit(node: str) -> None:
            color[node] = gray
            for dep in self._deps.get(node, ()):
                if color.get(dep, white) == gray:
                    raise DependencyError(f"Circular dependency involving '{node}' -> '{dep}'")
                if color.get(dep, white) == white:
                    visit(dep)
            color[node] = black

        for node in self._deps:
            if color.get(node, white) == white:
                visit(node)


_dependency_manager: DependencyManager | None = None


def get_dependency_manager() -> DependencyManager:
    global _dependency_manager
    if _dependency_manager is None:
        _dependency_manager = DependencyManager()
    return _dependency_manager
