"""Backup and recovery manager for database and files."""

from __future__ import annotations

import json
import logging
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from backend.utils.uuid_utils import generate_uuid

logger = logging.getLogger(__name__)


class BackupType(StrEnum):
    DATABASE = "database"
    FILES = "files"
    FULL = "full"


class BackupStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BackupManifest:
    id: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    completed_at: datetime | None = None
    file_path: str = ""
    file_size: int = 0
    checksum: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class BackupManager:
    """Manages backup and recovery operations."""

    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self._manifests: dict[str, BackupManifest] = {}

    def _generate_manifest_id(self) -> str:
        return generate_uuid()

    async def backup_database(
        self,
        db_url: str,
        metadata: dict[str, Any] | None = None,
    ) -> BackupManifest:
        manifest = BackupManifest(
            id=self._generate_manifest_id(),
            backup_type=BackupType.DATABASE,
            status=BackupStatus.RUNNING,
            created_at=datetime.now(UTC),
            metadata=metadata or {},
        )
        self._manifests[manifest.id] = manifest

        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"db_backup_{timestamp}.sql"
            file_path = self.backup_dir / filename

            # For PostgreSQL, use pg_dump
            if "postgresql" in db_url:
                import asyncio
                import subprocess

                cmd = [
                    "pg_dump",
                    "--no-owner",
                    "--no-acl",
                    "-f", str(file_path),
                    db_url.replace("+asyncpg", "").replace("+psycopg2", ""),
                ]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if proc.returncode != 0:
                    raise RuntimeError(f"pg_dump failed: {stderr.decode()}")
            else:
                # For SQLite, just copy the file
                if "sqlite" in db_url:
                    import re
                    match = re.search(r"///(.+)", db_url)
                    if match:
                        src = Path(match.group(1))
                        if src.exists():
                            shutil.copy2(src, file_path)
                        else:
                            raise FileNotFoundError(f"SQLite database not found: {src}")
                else:
                    # Generic: create a JSON export marker
                    with open(file_path, "w") as f:
                        json.dump({"type": "database", "url": db_url, "timestamp": timestamp}, f)

            manifest.file_path = str(file_path)
            manifest.file_size = file_path.stat().st_size if file_path.exists() else 0
            manifest.status = BackupStatus.COMPLETED
            manifest.completed_at = datetime.now(UTC)
            manifest.checksum = self._calculate_checksum(file_path)

            logger.info("Database backup completed: %s", manifest.id)
            return manifest

        except Exception as e:
            manifest.status = BackupStatus.FAILED
            manifest.error = str(e)
            manifest.completed_at = datetime.now(UTC)
            logger.error("Database backup failed: %s — %s", manifest.id, e)
            return manifest

    async def backup_files(
        self,
        source_paths: list[str],
        metadata: dict[str, Any] | None = None,
    ) -> BackupManifest:
        manifest = BackupManifest(
            id=self._generate_manifest_id(),
            backup_type=BackupType.FILES,
            status=BackupStatus.RUNNING,
            created_at=datetime.now(UTC),
            metadata=metadata or {},
        )
        self._manifests[manifest.id] = manifest

        try:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            backup_name = f"files_backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)

            total_size = 0
            for src_path in source_paths:
                src = Path(src_path)
                if src.is_file():
                    dest = backup_path / src.name
                    shutil.copy2(src, dest)
                    total_size += dest.stat().st_size
                elif src.is_dir():
                    dest = backup_path / src.name
                    shutil.copytree(src, dest, dirs_exist_ok=True)
                    total_size += sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())

            # Create archive
            archive_path = self.backup_dir / f"{backup_name}.tar.gz"
            shutil.make_archive(str(backup_path), "gztar", backup_path.parent, backup_path.name)
            shutil.rmtree(backup_path)

            manifest.file_path = str(archive_path) if archive_path.exists() else str(backup_path)
            manifest.file_size = total_size
            manifest.status = BackupStatus.COMPLETED
            manifest.completed_at = datetime.now(UTC)
            manifest.checksum = self._calculate_checksum(Path(manifest.file_path))

            logger.info("Files backup completed: %s (%d bytes)", manifest.id, total_size)
            return manifest

        except Exception as e:
            manifest.status = BackupStatus.FAILED
            manifest.error = str(e)
            manifest.completed_at = datetime.now(UTC)
            logger.error("Files backup failed: %s — %s", manifest.id, e)
            return manifest

    async def backup_full(
        self,
        db_url: str,
        source_paths: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BackupManifest:
        manifest = BackupManifest(
            id=self._generate_manifest_id(),
            backup_type=BackupType.FULL,
            status=BackupStatus.RUNNING,
            created_at=datetime.now(UTC),
            metadata=metadata or {},
        )
        self._manifests[manifest.id] = manifest

        try:
            results = {}
            db_result = await self.backup_database(db_url, metadata)
            results["database"] = {
                "id": db_result.id,
                "status": db_result.status.value,
                "file_path": db_result.file_path,
            }

            if source_paths:
                files_result = await self.backup_files(source_paths, metadata)
                results["files"] = {
                    "id": files_result.id,
                    "status": files_result.status.value,
                    "file_path": files_result.file_path,
                }

            manifest.metadata["results"] = results
            manifest.status = BackupStatus.COMPLETED
            manifest.completed_at = datetime.now(UTC)

            logger.info("Full backup completed: %s", manifest.id)
            return manifest

        except Exception as e:
            manifest.status = BackupStatus.FAILED
            manifest.error = str(e)
            manifest.completed_at = datetime.now(UTC)
            logger.error("Full backup failed: %s — %s", manifest.id, e)
            return manifest

    def get_manifest(self, backup_id: str) -> BackupManifest | None:
        return self._manifests.get(backup_id)

    def list_manifests(
        self,
        backup_type: BackupType | None = None,
        limit: int = 50,
    ) -> list[BackupManifest]:
        manifests = list(self._manifests.values())
        if backup_type:
            manifests = [m for m in manifests if m.backup_type == backup_type]
        return sorted(manifests, key=lambda m: m.created_at, reverse=True)[:limit]

    async def restore_database(self, backup_id: str, db_url: str) -> bool:
        manifest = self._manifests.get(backup_id)
        if not manifest or manifest.status != BackupStatus.COMPLETED:
            return False

        file_path = Path(manifest.file_path)
        if not file_path.exists():
            return False

        try:
            if "postgresql" in db_url:
                import asyncio

                cmd = [
                    "psql",
                    "-d", db_url.replace("+asyncpg", "").replace("+psycopg2", ""),
                    "-f", str(file_path),
                ]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                return proc.returncode == 0
            elif "sqlite" in db_url:
                import re
                match = re.search(r"///(.+)", db_url)
                if match:
                    dest = Path(match.group(1))
                    shutil.copy2(file_path, dest)
                    return True
            return False
        except Exception as e:
            logger.error("Database restore failed: %s", e)
            return False

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_backups": len(self._manifests),
            "by_type": {
                bt.value: sum(1 for m in self._manifests.values() if m.backup_type == bt)
                for bt in BackupType
            },
            "by_status": {
                bs.value: sum(1 for m in self._manifests.values() if m.status == bs)
                for bs in BackupStatus
            },
            "backup_dir": str(self.backup_dir),
        }

    @staticmethod
    def _calculate_checksum(file_path: Path) -> str:
        import hashlib
        if not file_path.exists():
            return ""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()


backup_manager = BackupManager()
