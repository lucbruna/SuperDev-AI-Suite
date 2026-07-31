"""
Admin Layout
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class AdminMenuItem:
    label: str
    icon: str = ""
    path: str = ""
    permission: str = ""


class AdminLayout:
    def __init__(self):
        self.menu_items: list[AdminMenuItem] = []
        self.user_permissions: list[str] = []

    def has_permission(self, permission: str) -> bool:
        return permission in self.user_permissions or "admin" in self.user_permissions

    def get_visible_items(self) -> list[AdminMenuItem]:
        return [item for item in self.menu_items if not item.permission or self.has_permission(item.permission)]

    def render(self) -> dict[str, Any]:
        return {"visibleItems": len(self.get_visible_items()), "totalItems": len(self.menu_items)}
