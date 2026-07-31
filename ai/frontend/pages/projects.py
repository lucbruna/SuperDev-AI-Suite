"""
Projects Page
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ProjectFilter:
    status: str | None = None
    search: str = ""
    sort_by: str = "updated_at"
    sort_dir: str = "desc"


class ProjectsPage:
    def __init__(self):
        self.projects: list[dict[str, Any]] = []
        self.filter = ProjectFilter()
        self.selected_ids: list[str] = []
        self.view_mode: str = "grid"

    def set_filter(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self.filter, k):
                setattr(self.filter, k, v)

    def toggle_select(self, project_id: str) -> None:
        if project_id in self.selected_ids:
            self.selected_ids.remove(project_id)
        else:
            self.selected_ids.append(project_id)

    def select_all(self) -> None:
        self.selected_ids = [p.get("id") for p in self.projects]

    def clear_selection(self) -> None:
        self.selected_ids = []

    def render(self) -> dict[str, Any]:
        return {"projectCount": len(self.projects), "selectedCount": len(self.selected_ids), "viewMode": self.view_mode}
