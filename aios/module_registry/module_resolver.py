"""ModuleResolver: validates dependencies/versions and computes load order."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from aios.module_registry.module import Module
from aios.module_registry.module_dependency_manager import ModuleDependencyManager
from aios.module_registry.module_version import ModuleVersion

_DEP_RE = re.compile(r"^([A-Za-z0-9_.\-]+)\s*(==|!=|>=|<=|>|<|~=)?\s*([0-9][\w.\-]*)?$")


@dataclass
class ModuleResolution:
    resolved: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    cycle: bool = False

    @property
    def ok(self) -> bool:
        return not self.missing and not self.conflicts and not self.cycle

    def to_dict(self) -> dict[str, Any]:
        return {
            "resolved": list(self.resolved),
            "missing": list(self.missing),
            "conflicts": list(self.conflicts),
            "cycle": self.cycle,
            "ok": self.ok,
        }


class ModuleResolver:
    def __init__(self, dependencies: ModuleDependencyManager | None = None) -> None:
        self.dependencies = dependencies if dependencies is not None else ModuleDependencyManager()

    @staticmethod
    def parse_dependency(dep: str) -> tuple[str, str, str]:
        match = _DEP_RE.match(str(dep).strip())
        if not match:
            return str(dep).strip(), "", ""
        return match.group(1), match.group(2) or "", match.group(3) or ""

    def resolve(self, modules: list[Module]) -> ModuleResolution:
        provided = {module.name: module for module in modules}
        graph: dict[str, list[str]] = {}
        missing: set[str] = set()
        conflicts: set[str] = set()

        for module in modules:
            dep_names: list[str] = []
            for dep in module.dependencies:
                dep_name, op, ver = self.parse_dependency(dep)
                if dep_name not in provided:
                    missing.add(dep_name)
                else:
                    dep_names.append(dep_name)
                    if op and ver:
                        actual = ModuleVersion(provided[dep_name].version)
                        if not ModuleVersion.satisfies(actual, f"{op}{ver}"):
                            conflicts.add(f"{dep_name}:{provided[dep_name].version} !{op}{ver}")
            graph[module.name] = dep_names
            self.dependencies.add_module(module.name, dep_names)

        try:
            order = self.dependencies.resolve_order(list(graph))
            cycle = False
        except ValueError:
            order = []
            cycle = True
        return ModuleResolution(
            resolved=order,
            missing=sorted(missing),
            conflicts=sorted(conflicts),
            cycle=cycle,
        )
