"""Factory Registry - Central registry for factory components."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class FactoryComponent:
    component_id: str
    name: str
    component_type: str = ""
    version: str = "1.0"
    status: str = "active"
    config: dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)


class FactoryRegistry:
    def __init__(self):
        self.components: dict[str, FactoryComponent] = {}
        self.dependencies: dict[str, list[str]] = {}

    def register(
        self, component_id: str, name: str, component_type: str = "", version: str = "1.0", **kwargs
    ) -> FactoryComponent:
        component = FactoryComponent(
            component_id=component_id, name=name, component_type=component_type, version=version, **kwargs
        )
        self.components[component_id] = component
        return component

    def get(self, component_id: str) -> FactoryComponent | None:
        return self.components.get(component_id)

    def update_status(self, component_id: str, status: str) -> bool:
        comp = self.components.get(component_id)
        if comp:
            comp.status = status
            return True
        return False

    def add_dependency(self, component_id: str, depends_on: str) -> None:
        self.dependencies.setdefault(component_id, []).append(depends_on)

    def get_dependencies(self, component_id: str) -> list[str]:
        return self.dependencies.get(component_id, [])

    def list_components(self, component_type: str = None) -> list[FactoryComponent]:
        comps = list(self.components.values())
        if component_type:
            comps = [c for c in comps if c.component_type == component_type]
        return comps

    def count(self) -> int:
        return len(self.components)
