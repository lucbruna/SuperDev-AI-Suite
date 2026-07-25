import uuid
from datetime import datetime, timezone
from typing import Optional

from .filesystem import WorkspaceFilesystem
from .snapshots import WorkspaceSnapshot


_restore_history: dict[str, list[dict]] = {}


class WorkspaceRestore:
    def __init__(
        self,
        filesystem: WorkspaceFilesystem,
        snapshot_manager: WorkspaceSnapshot,
    ) -> None:
        self._filesystem = filesystem
        self._snapshot_manager = snapshot_manager

    async def restore_from_snapshot(
        self, workspace_id: str, snapshot_id: str
    ) -> bool:
        snapshot = await self._snapshot_manager.get_snapshot(snapshot_id)
        if snapshot is None or snapshot["workspace_id"] != workspace_id:
            return False
        self._filesystem.set_all_files(snapshot["files"])
        await self._record_restore(
            workspace_id, snapshot_id, "full", None
        )
        return True

    async def restore_specific_files(
        self,
        workspace_id: str,
        snapshot_id: str,
        file_paths: list[str],
    ) -> bool:
        snapshot = await self._snapshot_manager.get_snapshot(snapshot_id)
        if snapshot is None or snapshot["workspace_id"] != workspace_id:
            return False
        for fp in file_paths:
            if fp in snapshot["files"]:
                await self._filesystem.write_file(
                    fp, snapshot["files"][fp]
                )
        await self._record_restore(
            workspace_id, snapshot_id, "partial", file_paths
        )
        return True

    async def get_restore_history(
        self, workspace_id: str
    ) -> list[dict]:
        return _restore_history.get(workspace_id, [])

    async def _record_restore(
        self,
        workspace_id: str,
        snapshot_id: str,
        restore_type: str,
        file_paths: Optional[list[str]],
    ) -> None:
        if workspace_id not in _restore_history:
            _restore_history[workspace_id] = []
        _restore_history[workspace_id].append(
            {
                "id": str(uuid.uuid4()),
                "workspace_id": workspace_id,
                "snapshot_id": snapshot_id,
                "type": restore_type,
                "file_paths": file_paths,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
