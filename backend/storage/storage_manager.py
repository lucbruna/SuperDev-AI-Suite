from __future__ import annotations

import os
import hashlib
from pathlib import Path
from typing import Any


class StorageManager:
    """Local file storage manager for artifacts and uploads."""

    def __init__(self, base_dir: str = "storage"):
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        safe_key = key.lstrip("/").replace("..", "")
        return self._base_dir / safe_key

    async def put(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> dict:
        path = self._get_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        checksum = hashlib.sha256(data).hexdigest()
        return {
            "key": key,
            "size": len(data),
            "checksum": checksum,
            "content_type": content_type,
        }

    async def get(self, key: str) -> bytes | None:
        path = self._get_path(key)
        if not path.exists():
            return None
        return path.read_bytes()

    async def delete(self, key: str) -> bool:
        path = self._get_path(key)
        if path.exists():
            path.unlink()
            return True
        return False

    async def exists(self, key: str) -> bool:
        return self._get_path(key).exists()

    async def list_keys(self, prefix: str = "") -> list[str]:
        base = self._get_path(prefix) if prefix else self._base_dir
        if not base.exists():
            return []
        return [str(p.relative_to(self._base_dir)) for p in base.rglob("*") if p.is_file()]

    async def get_size(self, key: str) -> int:
        path = self._get_path(key)
        if path.exists():
            return path.stat().st_size
        return 0


storage_manager = StorageManager()
