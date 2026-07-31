"""
Project Service
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Project:
    id: str
    name: str
    description: str = ""
    status: str = "active"
    members: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


class ProjectService:
    def __init__(self):
        self.projects: List[Project] = []
        
    def list(self) -> List[Project]:
        return self.projects
        
    def get(self, project_id: str) -> Optional[Project]:
        return next((p for p in self.projects if p.id == project_id), None)
        
    def create(self, name: str, description: str = "") -> Project:
        import uuid
        project = Project(id=str(uuid.uuid4()), name=name, description=description)
        self.projects.append(project)
        return project
        
    def update(self, project_id: str, **kwargs) -> Optional[Project]:
        project = self.get(project_id)
        if project:
            for k, v in kwargs.items():
                if hasattr(project, k):
                    setattr(project, k, v)
        return project
        
    def delete(self, project_id: str) -> bool:
        for i, p in enumerate(self.projects):
            if p.id == project_id:
                self.projects.pop(i)
                return True
        return False
        
    def render(self) -> Dict[str, Any]:
        return {"projects": [{"id": p.id, "name": p.name, "status": p.status} for p in self.projects]}
