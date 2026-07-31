"""Backup and recovery API routes."""

from __future__ import annotations

from typing import Any

from backend.backup.backup_manager import BackupType, backup_manager
from backend.dependencies import get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class DatabaseBackupRequest(BaseModel):
    db_url: str
    metadata: dict[str, Any] = {}


class FilesBackupRequest(BaseModel):
    source_paths: list[str]
    metadata: dict[str, Any] = {}


class FullBackupRequest(BaseModel):
    db_url: str
    source_paths: list[str] = []
    metadata: dict[str, Any] = {}


class RestoreRequest(BaseModel):
    backup_id: str
    db_url: str


@router.get("/")
async def list_backups(
    backup_type: str | None = None,
    limit: int = Query(default=50, le=200),
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    bt = BackupType(backup_type) if backup_type else None
    manifests = backup_manager.list_manifests(backup_type=bt, limit=limit)
    return {
        "backups": [
            {
                "id": m.id,
                "type": m.backup_type.value,
                "status": m.status.value,
                "created_at": m.created_at.isoformat(),
                "completed_at": m.completed_at.isoformat() if m.completed_at else None,
                "file_path": m.file_path,
                "file_size": m.file_size,
                "error": m.error,
            }
            for m in manifests
        ]
    }


@router.post("/database")
async def backup_database(
    request: DatabaseBackupRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    manifest = await backup_manager.backup_database(request.db_url, request.metadata)
    return {
        "id": manifest.id,
        "status": manifest.status.value,
        "file_path": manifest.file_path,
        "file_size": manifest.file_size,
    }


@router.post("/files")
async def backup_files(
    request: FilesBackupRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    manifest = await backup_manager.backup_files(request.source_paths, request.metadata)
    return {
        "id": manifest.id,
        "status": manifest.status.value,
        "file_path": manifest.file_path,
        "file_size": manifest.file_size,
    }


@router.post("/full")
async def backup_full(
    request: FullBackupRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    manifest = await backup_manager.backup_full(
        request.db_url, request.source_paths, request.metadata
    )
    return {
        "id": manifest.id,
        "status": manifest.status.value,
        "metadata": manifest.metadata,
    }


@router.post("/restore")
async def restore_backup(
    request: RestoreRequest,
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    success = await backup_manager.restore_database(request.backup_id, request.db_url)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restore failed. Check backup ID and database URL.",
        )
    return {"success": True, "backup_id": request.backup_id}


@router.get("/stats")
async def backup_stats(
    current_user: dict[str, Any] = Depends(get_current_active_user),
) -> dict[str, Any]:
    return backup_manager.get_stats()
