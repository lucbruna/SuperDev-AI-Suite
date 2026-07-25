import uuid
from datetime import datetime, timezone
from typing import Optional


_workspaces: dict[str, dict] = {}


class WorkspaceManager:
    async def create_workspace(
        self, name: str, project_id: str, template: Optional[str] = None
    ) -> str:
        workspace_id = str(uuid.uuid4())
        _workspaces[workspace_id] = {
            "id": workspace_id,
            "name": name,
            "project_id": project_id,
            "template": template,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return workspace_id

    async def get_workspace(self, workspace_id: str) -> Optional[dict]:
        return _workspaces.get(workspace_id)

    async def list_workspaces(self, project_id: str) -> list[dict]:
        return [
            w for w in _workspaces.values() if w["project_id"] == project_id
        ]

    async def delete_workspace(self, workspace_id: str) -> bool:
        return _workspaces.pop(workspace_id, None) is not None
