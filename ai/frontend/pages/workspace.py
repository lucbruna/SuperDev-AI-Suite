"""
Workspace Page
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class WorkspaceTab:
    id: str
    title: str
    file_path: str = ""
    modified: bool = False
    active: bool = False


class WorkspacePage:
    def __init__(self):
        self.tabs: list[WorkspaceTab] = []
        self.active_tab_id: str | None = None
        self.layout: str = "horizontal"
        self.show_terminal: bool = True
        self.show_file_tree: bool = True
        self.show_ai_panel: bool = True

    def open_tab(self, tab: WorkspaceTab) -> None:
        existing = next((t for t in self.tabs if t.file_path == tab.file_path), None)
        if existing:
            self.active_tab_id = existing.id
        else:
            self.tabs.append(tab)
            self.active_tab_id = tab.id

    def close_tab(self, tab_id: str) -> None:
        self.tabs = [t for t in self.tabs if t.id != tab_id]
        if self.active_tab_id == tab_id:
            self.active_tab_id = self.tabs[-1].id if self.tabs else None

    def toggle_panel(self, panel: str) -> None:
        if panel == "terminal":
            self.show_terminal = not self.show_terminal
        elif panel == "fileTree":
            self.show_file_tree = not self.show_file_tree
        elif panel == "ai":
            self.show_ai_panel = not self.show_ai_panel

    def render(self) -> dict[str, Any]:
        return {"tabs": [{"id": t.id, "title": t.title, "modified": t.modified} for t in self.tabs], "activeTab": self.active_tab_id}
