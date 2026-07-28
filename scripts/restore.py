from __future__ import annotations

from pathlib import Path
from typing import Any

from scripts.backup import BackupManager


class RestoreManager:
    def __init__(self, backup_dir: str | None = None):
        self._backup = BackupManager(backup_dir)

    def list_restore_points(self) -> list[dict[str, Any]]:
        return self._backup.list_backups()

    def create_restore_point(self, name: str | None = None) -> dict[str, Any]:
        return self._backup.create_backup(name)

    def restore(self, backup_name: str, target_dir: str | None = None, selective: list[str] | None = None) -> dict[str, Any]:
        result = self._backup.restore_backup(backup_name, target_dir)
        if not result["success"]:
            return result
        restore_path = Path(result["path"])
        if selective:
            for item in restore_path.rglob("*"):
                if item.is_file():
                    should_keep = any(s in str(item) for s in selective)
                    if not should_keep:
                        item.unlink()
            result["selective"] = selective
        return result

    def preview_restore(self, backup_name: str) -> dict[str, Any]:
        backup_file = Path(self._backup._backup_dir) / f"{backup_name}.tar.gz"
        if not backup_file.exists():
            return {"success": False, "error": f"Backup not found: {backup_name}"}
        import tarfile
        files = []
        with tarfile.open(str(backup_file), "r:gz") as tar:
            for member in tar.getmembers():
                if member.isfile():
                    files.append({"path": member.name, "size": member.size, "modified": member.mtime})
        return {"success": True, "backup": backup_name, "file_count": len(files), "total_size": sum(f["size"] for f in files), "files": files[:50]}

    def verify_backup(self, backup_name: str) -> dict[str, Any]:
        backup_file = Path(self._backup._backup_dir) / f"{backup_name}.tar.gz"
        if not backup_file.exists():
            return {"success": False, "error": "Backup not found"}
        import tarfile
        try:
            with tarfile.open(str(backup_file), "r:gz") as tar:
                members = tar.getmembers()
                corrupt = [m for m in members if m.size == 0 and not m.isdir()]
                return {"success": True, "valid": len(corrupt) == 0, "total_files": len(members), "corrupt_files": len(corrupt), "size": backup_file.stat().st_size}
        except Exception as e:
            return {"success": False, "error": str(e)}