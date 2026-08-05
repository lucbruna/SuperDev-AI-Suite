"""Cloud Backup — backup plans and retention (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_RETENTION_DAYS = 30


class CloudBackup:
    """Manage backup schedules and retention policies."""

    def __init__(self) -> None:
        self._backups: list[dict] = []

    def create_backup(self, *, label: str = "", size_mb: float = 0.0) -> dict:
        """Record a backup snapshot."""
        backup = {"label": label or "snapshot", "size_mb": size_mb, "retention_days": _RETENTION_DAYS}
        self._backups.append(backup)
        return backup

    def next_retention(self) -> dict:
        """Return the oldest backup past its retention window (simulated)."""
        expired = [b for b in self._backups if b.get("retention_days", 0) <= 0]
        return {"expired": expired, "count": len(expired)}

    def stats(self) -> dict[str, int | float]:
        return {"backups": len(self._backups), "total_size_mb": round(sum(b["size_mb"] for b in self._backups), 2)}


_BACKUP: CloudBackup | None = None


def get_cloud_backup() -> CloudBackup:
    """Get the module-level singleton cloud backup manager."""
    global _BACKUP
    if _BACKUP is None:
        _BACKUP = CloudBackup()
    return _BACKUP
