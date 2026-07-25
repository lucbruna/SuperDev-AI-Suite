import uuid
from datetime import datetime, timezone
from copy import deepcopy
from typing import Optional

from .filesystem import WorkspaceFilesystem


_snapshots: dict[str, dict] = {}


class WorkspaceSnapshot:
    def __init__(self, filesystem: WorkspaceFilesystem) -> None:
        self._filesystem = filesystem

    async def create_snapshot(self, workspace_id: str) -> str:
        snapshot_id = str(uuid.uuid4())
        _snapshots[snapshot_id] = {
            "id": snapshot_id,
            "workspace_id": workspace_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "files": deepcopy(self._filesystem.get_all_files()),
        }
        return snapshot_id

    async def list_snapshots(self, workspace_id: str) -> list[dict]:
        return [
            s
            for s in _snapshots.values()
            if s["workspace_id"] == workspace_id
        ]

    async def get_snapshot(self, snapshot_id: str) -> Optional[dict]:
        return _snapshots.get(snapshot_id)

    async def restore_snapshot(self, snapshot_id: str) -> bool:
        snapshot = _snapshots.get(snapshot_id)
        if snapshot is None:
            return False
        self._filesystem.set_all_files(snapshot["files"])
        return True

    async def delete_snapshot(self, snapshot_id: str) -> bool:
        return _snapshots.pop(snapshot_id, None) is not None
