"""BI Registry — Central registry for BI components."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class BIComponent:
    component_id: str
    name: str
    component_type: str = ""
    version: str = "1.0"
    status: str = "active"
    config: dict[str, Any] = field(default_factory=dict)
    registered_at: datetime = field(default_factory=datetime.now)


class BIRegistry:
    def __init__(self):
        self.components: dict[str, BIComponent] = {}
        self.dependencies: dict[str, list[str]] = {}

    def register(self, component_id: str, name: str, component_type: str = "", version: str = "1.0", **kwargs) -> BIComponent:
        component = BIComponent(component_id=component_id, name=name, component_type=component_type, version=version, **kwargs)
        self.components[component_id] = component
        return component

    def get(self, component_id: str) -> BIComponent | None:
        return self.components.get(component_id)

    def get_by_type(self, component_type: str) -> list[BIComponent]:
        return [c for c in self.components.values() if c.component_type == component_type]

    def deregister(self, component_id: str) -> bool:
        if component_id in self.components:
            del self.components[component_id]
            return True
        return False

    def add_dependency(self, component_id: str, depends_on: str) -> None:
        self.dependencies.setdefault(component_id, []).append(depends_on)

    def get_dependencies(self, component_id: str) -> list[str]:
        return self.dependencies.get(component_id, [])

    def count(self) -> int:
        return len(self.components)
