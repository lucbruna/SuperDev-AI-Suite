from __future__ import annotations

from typing import Any


class UMLGenerator:
    """Generates UML diagram representations."""

    def __init__(self) -> None:
        self._classes: dict[str, list[str]] = {}
        self._relationships: list[dict[str, str]] = []

    def add_class(self, name: str, attributes: list[str]) -> str:
        self._classes[name] = attributes
        return name

    def get_class(self, name: str) -> list[str] | None:
        return self._classes.get(name)

    def remove_class(self, name: str) -> bool:
        if name in self._classes:
            del self._classes[name]
            return True
        return False

    @property
    def class_count(self) -> int:
        return len(self._classes)

    def add_relationship(self, from_class: str, to_class: str, rel_type: str) -> str:
        rel = {"from": from_class, "to": to_class, "type": rel_type}
        self._relationships.append(rel)
        return f"{from_class} -> {to_class} [{rel_type}]"

    def generate_plantuml(self) -> str:
        lines: list[str] = ["@startuml", ""]
        for cls_name, attrs in self._classes.items():
            lines.append(f"class {cls_name} {{")
            for attr in attrs:
                lines.append(f"  +{attr}")
            lines.append("}")
            lines.append("")
        for rel in self._relationships:
            arrow = "-->"
            if rel["type"] == "extends":
                arrow = "--|>"
            elif rel["type"] == "implements":
                arrow = "..|>"
            elif rel["type"] == "dependency":
                arrow = "..>"
            lines.append(f"{rel['from']} {arrow} {rel['to']}")
        lines.append("")
        lines.append("@enduml")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "classes": {k: v for k, v in self._classes.items()},
            "relationships": self._relationships,
            "class_count": self.class_count,
        }
