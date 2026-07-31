"""Project dashboard."""
from __future__ import annotations
from typing import Any, Dict, List

class ProjectDashboard:
    def __init__(self) -> None:
        self._projects: Dict[str, Dict[str, Any]] = {}
    def update_project(self, project_id: str, data: Dict[str, Any]) -> None:
        self._projects[project_id] = data
    def get_project(self, project_id: str) -> Dict[str, Any]:
        return self._projects.get(project_id, {})
    def list_projects(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in self._projects.items()]
    def get_build_status(self, project_id: str) -> str:
        return self._projects.get(project_id, {}).get("build_status", "unknown")
    def get_test_coverage(self, project_id: str) -> float:
        return self._projects.get(project_id, {}).get("test_coverage", 0.0)
    def get_summary(self) -> Dict[str, Any]:
        return {"projects": len(self._projects), "building": sum(1 for p in self._projects.values() if p.get("build_status") == "building")}
