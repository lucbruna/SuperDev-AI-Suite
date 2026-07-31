from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProjectState:
    """State for the active project context."""

    project_id: str | None = None
    name: str = ""
    status: str = "idle"
    current_file: str | None = None
    branches: list[str] = field(default_factory=list)
    env: str = "development"
    meta: dict[str, Any] = field(default_factory=dict)

    def activate(self, project_id: str, name: str, **meta: Any) -> None:
        self.project_id = project_id
        self.name = name
        self.status = "active"
        self.meta = dict(meta)

    def open_file(self, path: str) -> None:
        self.current_file = path

    def set_status(self, status: str) -> None:
        self.status = status

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "name": self.name,
            "status": self.status,
            "current_file": self.current_file,
            "branches": list(self.branches),
            "env": self.env,
            "meta": dict(self.meta),
        }
