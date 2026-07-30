from __future__ import annotations

from typing import Any


class ComponentModeler:
    """Models software components with responsibilities, interfaces, and dependencies."""

    def __init__(self) -> None:
        self._components: dict[str, dict[str, Any]] = {}

    def add_component(
        self,
        name: str,
        responsibility: str,
        interfaces: list[str],
        dependencies: list[str] | None = None,
    ) -> str:
        component = {
            "name": name,
            "responsibility": responsibility,
            "interfaces": interfaces,
            "dependencies": dependencies or [],
        }
        self._components[name] = component
        return name

    def get_component(self, name: str) -> dict[str, Any] | None:
        return self._components.get(name)

    def remove_component(self, name: str) -> bool:
        if name in self._components:
            del self._components[name]
            return True
        return False

    def list_components(self) -> list[dict[str, Any]]:
        return list(self._components.values())

    @property
    def component_count(self) -> int:
        return len(self._components)

    def to_dict(self) -> dict[str, Any]:
        return {
            "components": self._components,
            "component_count": self.component_count,
        }
