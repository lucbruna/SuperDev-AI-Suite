"""Dependency mapping."""
from __future__ import annotations


class DependencyMap:
    def __init__(self) -> None:
        self._deps: dict[str, set[str]] = {}
        self._reverse: dict[str, set[str]] = {}
    def add_dependency(self, source: str, target: str) -> None:
        self._deps.setdefault(source, set()).add(target)
        self._reverse.setdefault(target, set()).add(source)
    def remove_dependency(self, source: str, target: str) -> bool:
        if source in self._deps and target in self._deps[source]:
            self._deps[source].discard(target)
            self._reverse.get(target, set()).discard(source)
            return True
        return False
    def get_dependencies(self, service: str) -> list[str]:
        return list(self._deps.get(service, set()))
    def get_dependents(self, service: str) -> list[str]:
        return list(self._reverse.get(service, set()))
    def get_all_services(self) -> list[str]:
        all_svc = set(self._deps.keys()) | set(self._reverse.keys())
        return sorted(all_svc)
    def has_cycle(self) -> bool:
        visited: set[str] = set()
        path: set[str] = set()
        def dfs(node: str) -> bool:
            visited.add(node)
            path.add(node)
            for neighbor in self._deps.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in path:
                    return True
            path.discard(node)
            return False
        return any(dfs(n) for n in self._deps if n not in visited)
    def to_dict(self) -> dict[str, list[str]]:
        return {k: list(v) for k, v in self._deps.items()}
