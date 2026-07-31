"""
Admin Layout
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class AdminMenuItem:
    label: str
    icon: str = ""
    path: str = ""
    permission: str = ""


class AdminLayout:
    def __init__(self):
        self.menu_items: List[AdminMenuItem] = []
        self.user_permissions: List[str] = []
        
    def has_permission(self, permission: str) -> bool:
        return permission in self.user_permissions or "admin" in self.user_permissions
        
    def get_visible_items(self) -> List[AdminMenuItem]:
        return [item for item in self.menu_items if not item.permission or self.has_permission(item.permission)]
        
    def render(self) -> Dict[str, Any]:
        return {"visibleItems": len(self.get_visible_items()), "totalItems": len(self.menu_items)}
