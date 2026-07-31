"""
Developer Layout
"""
from typing import Dict, Any, List
from dataclasses import dataclass, field


class DeveloperLayout:
    def __init__(self):
        self.panels: Dict[str, bool] = {"fileTree": True, "terminal": True, "ai": True, "git": False}
        self.panel_sizes: Dict[str, int] = {"sidebar": 260, "terminal": 200, "ai": 300}
        
    def toggle_panel(self, panel: str) -> None:
        self.panels[panel] = not self.panels.get(panel, False)
        
    def set_panel_size(self, panel: str, size: int) -> None:
        self.panels[panel] = size
        
    def render(self) -> Dict[str, Any]:
        return {"panels": self.panels, "sizes": self.panel_sizes}
