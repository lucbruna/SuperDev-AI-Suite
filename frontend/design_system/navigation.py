from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NavItem:
    """A single navigation item."""

    label: str
    route: str
    icon: str = ""
    section: str = "main"
    permission: str | None = None
    badge: str | None = None


@dataclass
class NavStructure:
    """Navigation tree definition."""

    brand: str
    items: list[NavItem] = field(default_factory=list)
    collapsed: bool = False


class Navigation:
    """Builds navigation structures for header and sidebar."""

    def __init__(self) -> None:
        self._structures: dict[str, NavStructure] = {}

    def register(self, name: str, structure: NavStructure) -> None:
        self._structures[name] = structure

    def get(self, name: str) -> NavStructure:
        if name not in self._structures:
            raise KeyError(f"unknown navigation structure: {name}")
        return self._structures[name]

    def default_structure(self) -> NavStructure:
        return NavStructure(
            brand="SuperDev",
            items=[
                NavItem("Dashboard", "/dashboard", "dashboard"),
                NavItem("Agents", "/agents", "agents"),
                NavItem("Projects", "/projects", "projects"),
                NavItem("Workflows", "/workflows", "workflows"),
                NavItem("Editor", "/editor", "editor"),
                NavItem("Monitoring", "/monitoring", "monitoring"),
            ],
        )

    def build(self, name: str, **props: Any) -> dict[str, Any]:
        return {"type": "navigation", "name": name, **vars(self.get(name)), "props": props}

    def items_by_section(self, name: str) -> dict[str, list[NavItem]]:
        sections: dict[str, list[NavItem]] = {}
        for item in self.get(name).items:
            sections.setdefault(item.section, []).append(item)
        return sections
