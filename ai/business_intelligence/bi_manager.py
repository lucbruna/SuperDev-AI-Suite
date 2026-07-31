"""BI Manager — Project and lifecycle management for BI operations."""
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib


class BIProject:
    def __init__(self, project_id: str, name: str, description: str = ""):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.status = "active"
        self.created_at = datetime.now()
        self.metadata: Dict[str, Any] = {}


class BIManager:
    def __init__(self):
        self._projects: Dict[str, BIProject] = {}
        self._artifacts: Dict[str, List[Dict[str, Any]]] = {}
        self._approvals: Dict[str, Dict[str, Any]] = {}

    def create_project(self, name: str, description: str = "") -> BIProject:
        project_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        project = BIProject(project_id=project_id, name=name, description=description)
        self._projects[project_id] = project
        return project

    def get_project(self, project_id: str) -> Optional[BIProject]:
        return self._projects.get(project_id)

    def list_projects(self) -> List[BIProject]:
        return list(self._projects.values())

    def add_artifact(self, project_id: str, artifact_type: str, content: Any) -> Dict[str, Any]:
        artifact = {
            "type": artifact_type,
            "content": content,
            "created_at": datetime.now().isoformat(),
        }
        self._artifacts.setdefault(project_id, []).append(artifact)
        return artifact

    def get_artifacts(self, project_id: str) -> List[Dict[str, Any]]:
        return self._artifacts.get(project_id, [])

    def approve(self, project_id: str, approver: str) -> bool:
        if project_id in self._projects:
            self._approvals[project_id] = {"approver": approver, "timestamp": datetime.now().isoformat()}
            return True
        return False

    def count(self) -> int:
        return len(self._projects)
