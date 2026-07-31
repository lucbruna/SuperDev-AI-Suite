"""
Security Registry
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SecurityComponent:
    name: str
    component_type: str
    status: str = "active"
    config: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class SecurityRegistry:
    def __init__(self):
        self.components: dict[str, SecurityComponent] = {}
        self.groups: dict[str, list[str]] = {}

    def register(self, name: str, component_type: str, config: dict[str, Any] = None) -> SecurityComponent:
        component = SecurityComponent(name=name, component_type=component_type, config=config or {})
        self.components[name] = component
        return component

    def unregister(self, name: str) -> bool:
        if name in self.components:
            del self.components[name]
            return True
        return False

    def get(self, name: str) -> SecurityComponent | None:
        return self.components.get(name)

    def list_all(self) -> list[SecurityComponent]:
        return list(self.components.values())

    def list_by_type(self, component_type: str) -> list[SecurityComponent]:
        return [c for c in self.components.values() if c.component_type == component_type]

    def update_status(self, name: str, status: str) -> bool:
        component = self.get(name)
        if component:
            component.status = status
            return True
        return False

    def add_to_group(self, group: str, component_name: str) -> None:
        if group not in self.groups:
            self.groups[group] = []
        if component_name not in self.groups[group]:
            self.groups[group].append(component_name)

    def get_group(self, group: str) -> list[SecurityComponent]:
        names = self.groups.get(group, [])
        return [self.components[n] for n in names if n in self.components]

    def count(self) -> int:
        return len(self.components)
