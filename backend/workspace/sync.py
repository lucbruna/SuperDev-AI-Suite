from pathlib import Path

from .filesystem import WorkspaceFilesystem


class WorkspaceSync:
    def __init__(self, filesystem: WorkspaceFilesystem) -> None:
        self._filesystem = filesystem
        self._workspaces: dict[str, WorkspaceFilesystem] = {}

    def _get_fs(self, workspace_id: str) -> WorkspaceFilesystem:
        if workspace_id not in self._workspaces:
            self._workspaces[workspace_id] = WorkspaceFilesystem()
        return self._workspaces[workspace_id]

    async def sync_to_disk(self, workspace_id: str, base_path: str) -> None:
        fs = self._get_fs(workspace_id)
        base = Path(base_path)
        base.mkdir(parents=True, exist_ok=True)

        for rel_path, content in fs.get_all_files().items():
            full_path = base / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")

    async def sync_from_disk(self, workspace_id: str, base_path: str) -> None:
        fs = self._get_fs(workspace_id)
        base = Path(base_path)
        if not base.exists():
            return

        files: dict[str, str] = {}
        for entry in base.rglob("*"):
            if entry.is_file():
                rel = str(entry.relative_to(base))
                files[rel] = entry.read_text(encoding="utf-8")
        fs.set_all_files(files)

    async def diff(
        self, workspace_id: str, base_path: str
    ) -> list[dict[str, str]]:
        fs = self._get_fs(workspace_id)
        base = Path(base_path)
        changes: list[dict[str, str]] = []
        memory_files = set(fs.get_all_files().keys())

        disk_files: set[str] = set()
        if base.exists():
            for entry in base.rglob("*"):
                if entry.is_file():
                    rel = str(entry.relative_to(base))
                    disk_files.add(rel)
                    disk_content = entry.read_text(encoding="utf-8")
                    memory_content = await fs.read_file(rel)
                    if memory_content is None:
                        changes.append(
                            {"file": rel, "type": "deleted"}
                        )
                    elif memory_content != disk_content:
                        changes.append(
                            {"file": rel, "type": "modified"}
                        )

        for f in memory_files:
            if f not in disk_files:
                changes.append({"file": f, "type": "added"})

        return changes
