import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


class BackupManager:
    def __init__(self, backup_dir: str | None = None):
        self._backup_dir = Path(backup_dir or Path.home() / ".superdev" / "backups")
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._sources = {
            "database": {"type": "postgres", "enabled": True},
            "config": {"type": "directory", "path": str(Path.home() / ".superdev"), "enabled": True},
            "workspaces": {"type": "directory", "path": "./workspaces", "enabled": False},
        }

    def list_backups(self) -> list[dict[str, Any]]:
        backups = []
        for f in sorted(self._backup_dir.glob("*"), reverse=True):
            if f.is_file():
                backups.append({
                    "name": f.name,
                    "size": f.stat().st_size,
                    "created_at": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                    "path": str(f),
                })
        return backups

    def create_backup(self, name: str | None = None) -> dict[str, Any]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"backup_{timestamp}"
        backup_path = self._backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        results = []
        for source_name, source_config in self._sources.items():
            if not source_config.get("enabled", False):
                continue
            if source_config["type"] == "postgres":
                result = self._backup_postgres(backup_path, source_name)
            elif source_config["type"] == "directory":
                result = self._backup_directory(backup_path, source_name, source_config["path"])
            else:
                result = {"source": source_name, "success": False, "error": f"Unknown type: {source_config['type']}"}
            results.append(result)
        archive_path = self._compress_backup(backup_path)
        shutil.rmtree(backup_path)
        return {"name": backup_name, "path": archive_path, "timestamp": timestamp, "results": results}

    def _backup_postgres(self, backup_path: Path, source_name: str) -> dict[str, Any]:
        db_name = os.getenv("DB_NAME", "superdev")
        db_user = os.getenv("DB_USER", "superdev")
        output_file = backup_path / f"{source_name}.sql"
        try:
            result = subprocess.run(
                ["pg_dump", f"--dbname=postgresql://{db_user}@localhost/{db_name}", f"--file={output_file}"],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                return {"source": source_name, "success": True, "file": str(output_file), "size": output_file.stat().st_size}
            return {"source": source_name, "success": False, "error": result.stderr[:200]}
        except FileNotFoundError:
            return {"source": source_name, "success": False, "error": "pg_dump not found"}
        except subprocess.TimeoutExpired:
            return {"source": source_name, "success": False, "error": "Timeout"}

    def _backup_directory(self, backup_path: Path, source_name: str, dir_path: str) -> dict[str, Any]:
        src = Path(dir_path)
        if not src.exists():
            return {"source": source_name, "success": False, "error": f"Directory not found: {dir_path}"}
        dest = backup_path / source_name
        try:
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".git"))
            size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
            return {"source": source_name, "success": True, "path": str(dest), "size": size}
        except Exception as e:
            return {"source": source_name, "success": False, "error": str(e)[:200]}

    def _compress_backup(self, backup_path: Path) -> str:
        archive_name = f"{backup_path.name}.tar.gz"
        archive_path = self._backup_dir / archive_name
        import tarfile
        with tarfile.open(str(archive_path), "w:gz") as tar:
            tar.add(str(backup_path), arcname=backup_path.name)
        return str(archive_path)

    def restore_backup(self, backup_name: str, target_dir: str | None = None) -> dict[str, Any]:
        backup_file = self._backup_dir / backup_name
        if not backup_file.exists():
            backup_file = self._backup_dir / f"{backup_name}.tar.gz"
        if not backup_file.exists():
            return {"success": False, "error": f"Backup not found: {backup_name}"}
        import tarfile
        restore_dir = Path(target_dir) if target_dir else self._backup_dir / "restore"
        restore_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(str(backup_file), "r:gz") as tar:
            tar.extractall(path=str(restore_dir))
        return {"success": True, "path": str(restore_dir), "files": len(list(restore_dir.rglob("*")))}

    def delete_backup(self, backup_name: str) -> bool:
        paths = [self._backup_dir / backup_name, self._backup_dir / f"{backup_name}.tar.gz"]
        deleted = False
        for p in paths:
            if p.exists():
                p.unlink()
                deleted = True
        return deleted

    def cleanup_old(self, max_age_days: int = 30) -> int:
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)
        deleted = 0
        for f in self._backup_dir.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
                deleted += 1
        return deleted