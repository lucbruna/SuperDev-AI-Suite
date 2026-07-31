from __future__ import annotations

from typing import Any


class DependencyScanner:
    """Scans dependencies for known vulnerabilities."""

    def __init__(self) -> None:
        self._dependencies: dict[str, dict[str, Any]] = {}

    def add_dependency(
        self,
        name: str,
        version: str,
        known_vulns: list[str] | None = None,
    ) -> str:
        self._dependencies[name] = {
            "name": name,
            "version": version,
            "known_vulns": known_vulns or [],
        }
        return name

    def get_dependency(self, name: str) -> dict[str, Any] | None:
        return self._dependencies.get(name)

    def remove_dependency(self, name: str) -> bool:
        if name in self._dependencies:
            del self._dependencies[name]
            return True
        return False

    def list_dependencies(self) -> list[dict[str, Any]]:
        return list(self._dependencies.values())

    def scan_vulnerabilities(self) -> list[dict[str, Any]]:
        return [dep for dep in self._dependencies.values() if dep["known_vulns"]]

    @property
    def dependency_count(self) -> int:
        return len(self._dependencies)

    @property
    def vulnerable_count(self) -> int:
        return sum(1 for d in self._dependencies.values() if d["known_vulns"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "dependencies": list(self._dependencies.values()),
            "dependency_count": self.dependency_count,
            "vulnerable_count": self.vulnerable_count,
        }
