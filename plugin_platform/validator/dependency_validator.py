from __future__ import annotations

from typing import Any


class DependencyValidator:
    def check_dependencies(
        self, manifest: dict[str, Any], installed_plugins: dict[str, dict[str, Any]]
    ) -> list[tuple[str, bool, str]]:
        results: list[tuple[str, bool, str]] = []
        dependencies = manifest.get("dependencies", [])

        if not dependencies:
            return results

        for dep in dependencies:
            if isinstance(dep, str):
                dep_name = dep
                dep_version = None
            elif isinstance(dep, dict):
                dep_name = dep.get("name", "")
                dep_version = dep.get("version")
            else:
                results.append((str(dep), False, f"Invalid dependency format: {dep}"))
                continue

            if not dep_name:
                results.append(("unknown", False, "Dependency name is empty"))
                continue

            if dep_name not in installed_plugins:
                results.append((dep_name, False, f"Dependency '{dep_name}' is not installed"))
                continue

            if dep_version:
                installed_manifest = installed_plugins[dep_name].get("manifest", {})
                installed_version = installed_manifest.get("version", "0.0.0")
                if self._compare_versions(installed_version, dep_version) < 0:
                    results.append((
                        dep_name, False,
                        f"Dependency '{dep_name}' version {installed_version} < required {dep_version}"
                    ))
                    continue

            results.append((dep_name, True, f"Dependency '{dep_name}' is satisfied"))

        return results

    @staticmethod
    def _compare_versions(v1: str, v2: str) -> int:
        def parse(v: str) -> tuple[int, ...]:
            parts = v.split(".")[:3]
            return tuple(int(p) if p.isdigit() else 0 for p in parts)
        p1 = parse(v1)
        p2 = parse(v2)
        if p1 < p2:
            return -1
        if p1 > p2:
            return 1
        return 0
