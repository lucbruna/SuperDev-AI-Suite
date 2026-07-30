from __future__ import annotations

from typing import Any


class ComponentGenerator:
    """Generates and manages frontend component definitions."""

    def __init__(self) -> None:
        self._components: dict[str, dict[str, Any]] = {}

    def add_component(
        self,
        name: str,
        props: list[str],
        template: str = "functional",
    ) -> str:
        self._components[name] = {
            "name": name,
            "props": props,
            "template": template,
        }
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

    def generate_component_code(self, name: str) -> str:
        comp = self._components.get(name)
        if comp is None:
            return f"// Component '{name}' not found"
        props_str = ", ".join(comp["props"])
        return (
            f"import React from 'react';\n\n"
            f"interface {name}Props {{\n"
            f"  {props_str}: any;\n"
            f"}}\n\n"
            f"const {name}: React.FC<{name}Props> = ({{ {props_str} }}) => {{\n"
            f"  return (\n"
            f"    <div className=\"{name.lower()}\">\n"
            f"      {{/* TODO: implement */}}\n"
            f"    </div>\n"
            f"  );\n"
            f"}};\n\n"
            f"export default {name};\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "components": list(self._components.values()),
            "component_count": self.component_count,
        }
