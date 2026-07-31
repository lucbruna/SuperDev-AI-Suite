"""Factory Manager - Project lifecycle management."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class ProjectArtifact:
    artifact_id: str
    project_id: str
    name: str
    artifact_type: str = ""
    content: Any = None
    path: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FactoryManager:
    def __init__(self):
        self.artifacts: Dict[str, List[ProjectArtifact]] = {}
        self.approvals: Dict[str, Dict[str, Any]] = {}

    def add_artifact(self, project_id: str, name: str, artifact_type: str = "", content: Any = None, path: str = "") -> ProjectArtifact:
        artifact_id = hashlib.sha256(f"{project_id}{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        artifact = ProjectArtifact(artifact_id=artifact_id, project_id=project_id, name=name, artifact_type=artifact_type, content=content, path=path)
        self.artifacts.setdefault(project_id, []).append(artifact)
        return artifact

    def get_artifacts(self, project_id: str) -> List[ProjectArtifact]:
        return self.artifacts.get(project_id, [])

    def request_approval(self, project_id: str, reviewer: str, notes: str = "") -> str:
        approval_id = hashlib.sha256(f"{project_id}{reviewer}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        self.approvals[approval_id] = {"project_id": project_id, "reviewer": reviewer, "notes": notes, "status": "pending", "timestamp": datetime.now().isoformat()}
        return approval_id

    def approve(self, approval_id: str, approved: bool = True, comment: str = "") -> bool:
        if approval_id in self.approvals:
            self.approvals[approval_id]["status"] = "approved" if approved else "rejected"
            self.approvals[approval_id]["comment"] = comment
            return True
        return False

    def get_approval(self, approval_id: str) -> Optional[Dict[str, Any]]:
        return self.approvals.get(approval_id)

    def count_artifacts(self, project_id: str) -> int:
        return len(self.artifacts.get(project_id, []))
