"""
Developer Layout
"""

from typing import Any


class DeveloperLayout:
    def __init__(self):
        self.panels: dict[str, bool] = {"fileTree": True, "terminal": True, "ai": True, "git": False}
        self.panel_sizes: dict[str, int] = {"sidebar": 260, "terminal": 200, "ai": 300}

    def toggle_panel(self, panel: str) -> None:
        self.panels[panel] = not self.panels.get(panel, False)

    def set_panel_size(self, panel: str, size: int) -> None:
        self.panels[panel] = size

    def render(self) -> dict[str, Any]:
        return {"panels": self.panels, "sizes": self.panel_sizes}
