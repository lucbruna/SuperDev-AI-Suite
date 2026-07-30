from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .memory_exceptions import MemoryBackupError


class BackupEntry:
    """Metadata for a single backup."""

    def __init__(
        self,
        backup_id: str,
        path: str,
        size_bytes: int = 0,
        entry_count: int = 0,
        compressed: bool = False,
    ):
        self._backup_id = backup_id
        self._path = path
        self._size_bytes = size_bytes
        self._entry_count = entry_count
        self._compressed = compressed
        self._created_at = time.time()

    @property
    def backup_id(self) -> str:
        return self._backup_id

    @property
    def path(self) -> str:
        return self._path

    @property
    def size_bytes(self) -> int:
        return self._size_bytes

    @property
    def entry_count(self) -> int:
        return self._entry_count

    @property
    def compressed(self) -> bool:
        return self._compressed

    @property
    def created_at(self) -> float:
        return self._created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backup_id": self._backup_id,
            "path": self._path,
            "size_bytes": self._size_bytes,
            "entry_count": self._entry_count,
            "compressed": self._compressed,
            "created_at": self._created_at,
        }


class MemoryBackup:
    """Backup functionality for the memory subsystem."""

    def __init__(self, backup_dir: str | Path):
        self._backup_dir = Path(backup_dir)
        self._backups: Dict[str, BackupEntry] = {}

    @property
    def backup_dir(self) -> Path:
        return self._backup_dir

    def create(self, backup_id: str, data: Dict[str, Any], compress: bool = True) -> BackupEntry:
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        path = self._backup_dir / f"{backup_id}_{int(time.time())}.backup"
        raw = json.dumps(data, indent=2)
        size = len(raw.encode("utf-8"))
        path.write_text(raw)
        entry = BackupEntry(
            backup_id=backup_id,
            path=str(path),
            size_bytes=size,
            entry_count=len(data),
            compressed=compress,
        )
        self._backups[backup_id] = entry
        return entry

    def load(self, backup_id: str) -> Dict[str, Any] | None:
        entry = self._backups.get(backup_id)
        if not entry:
            return None
        path = Path(entry.path)
        if not path.exists():
            del self._backups[backup_id]
            return None
        return json.loads(path.read_text())

    def list_backups(self) -> List[Dict[str, Any]]:
        backups = sorted(
            [b.to_dict() for b in self._backups.values()],
            key=lambda x: x["created_at"],
            reverse=True,
        )
        return backups

    def delete(self, backup_id: str) -> bool:
        entry = self._backups.pop(backup_id, None)
        if entry:
            path = Path(entry.path)
            if path.exists():
                path.unlink()
            return True
        return False

    def clear(self) -> None:
        for entry in self._backups.values():
            path = Path(entry.path)
            if path.exists():
                path.unlink()
        self._backups.clear()

    @property
    def count(self) -> int:
        return len(self._backups)

    @property
    def total_size_bytes(self) -> int:
        return sum(b.size_bytes for b in self._backups.values())
