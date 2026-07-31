"""
Project Store
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProjectState:
    projects: list[dict[str, Any]] = field(default_factory=list)
    selected_id: str | None = None
    loading: bool = False


class ProjectStore:
    def __init__(self):
        self.state = ProjectState()
        self.listeners: list = []

    def set_projects(self, projects: list[dict[str, Any]]) -> None:
        self.state.projects = projects
        self._notify()

    def select(self, project_id: str) -> None:
        self.state.selected_id = project_id
        self._notify()

    def add_project(self, project: dict[str, Any]) -> None:
        self.state.projects.append(project)
        self._notify()

    def remove_project(self, project_id: str) -> None:
        self.state.projects = [p for p in self.state.projects if p.get("id") != project_id]
        self._notify()

    def _notify(self) -> None:
        for cb in self.listeners:
            cb(self.state)

    def on_change(self, callback) -> None:
        self.listeners.append(callback)

    def render(self) -> dict[str, Any]:
        return {"projects": self.state.projects, "selectedId": self.state.selected_id, "loading": self.state.loading}
