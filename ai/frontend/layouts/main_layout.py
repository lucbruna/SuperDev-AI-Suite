"""
Main Layout
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MenuItem:
    label: str
    icon: str = ""
    path: str = ""
    children: list["MenuItem"] = field(default_factory=list)
    badge: str | None = None
    disabled: bool = False


class MainLayout:
    def __init__(self):
        self.menu_items: list[MenuItem] = []
        self.sidebar_collapsed: bool = False
        self.header_visible: bool = True
        self.footer_visible: bool = True
        self.current_path: str = "/"

    def toggle_sidebar(self) -> None:
        self.sidebar_collapsed = not self.sidebar_collapsed

    def set_path(self, path: str) -> None:
        self.current_path = path

    def add_menu_item(self, item: MenuItem) -> None:
        self.menu_items.append(item)

    def render(self) -> dict[str, Any]:
        return {
            "sidebarCollapsed": self.sidebar_collapsed,
            "headerVisible": self.header_visible,
            "menuItems": len(self.menu_items),
        }
