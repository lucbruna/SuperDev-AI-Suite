"""
Main Layout
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class MenuItem:
    label: str
    icon: str = ""
    path: str = ""
    children: List["MenuItem"] = field(default_factory=list)
    badge: Optional[str] = None
    disabled: bool = False


class MainLayout:
    def __init__(self):
        self.menu_items: List[MenuItem] = []
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
        
    def render(self) -> Dict[str, Any]:
        return {"sidebarCollapsed": self.sidebar_collapsed, "headerVisible": self.header_visible, "menuItems": len(self.menu_items)}
