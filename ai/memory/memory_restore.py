from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .memory_exceptions import MemoryRestoreError


class RestorePoint:
    """A restore point created before applying changes."""

    def __init__(self, restore_id: str, data: Dict[str, Any]):
        self._restore_id = restore_id
        self._data = dict(data)
        self._created_at = time.time()

    @property
    def restore_id(self) -> str:
        return self._restore_id

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)

    @property
    def created_at(self) -> float:
        return self._created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "restore_id": self._restore_id,
            "created_at": self._created_at,
        }


class MemoryRestore:
    """Restore functionality for recovering memory state."""

    def __init__(self, restore_dir: str | Path | None = None):
        self._restore_dir = Path(restore_dir) if restore_dir else None
        self._points: Dict[str, RestorePoint] = {}

    def create_point(self, restore_id: str, data: Dict[str, Any]) -> RestorePoint:
        point = RestorePoint(restore_id, data)
        self._points[restore_id] = point
        if self._restore_dir:
            self._write_to_disk(point)
        return point

    def restore(self, restore_id: str) -> Dict[str, Any] | None:
        point = self._points.get(restore_id)
        if point:
            return point.data
        if self._restore_dir:
            return self._read_from_disk(restore_id)
        return None

    def list_points(self) -> List[Dict[str, Any]]:
        points = [p.to_dict() for p in self._points.values()]
        points.sort(key=lambda x: x["created_at"], reverse=True)
        return points

    def delete_point(self, restore_id: str) -> bool:
        point = self._points.pop(restore_id, None)
        if point and self._restore_dir:
            self._delete_from_disk(restore_id)
        return point is not None

    def rollback(self, restore_id: str, current_data: Dict[str, Any]) -> Dict[str, Any] | None:
        previous = self.restore(restore_id)
        if previous is None:
            return None
        point = RestorePoint(f"pre_rollback_{restore_id}_{int(time.time())}", current_data)
        self._points[point.restore_id] = point
        return previous

    def clear(self) -> None:
        self._points.clear()

    def _write_to_disk(self, point: RestorePoint) -> None:
        if not self._restore_dir:
            return
        self._restore_dir.mkdir(parents=True, exist_ok=True)
        path = self._restore_dir / f"{point.restore_id}.restore"
        path.write_text(json.dumps({"restore_id": point.restore_id, "data": point.data}, indent=2))

    def _read_from_disk(self, restore_id: str) -> Dict[str, Any] | None:
        if not self._restore_dir:
            return None
        path = self._restore_dir / f"{restore_id}.restore"
        if path.exists():
            data = json.loads(path.read_text())
            return data.get("data")
        return None

    def _delete_from_disk(self, restore_id: str) -> None:
        if not self._restore_dir:
            return
        path = self._restore_dir / f"{restore_id}.restore"
        path.unlink(missing_ok=True)

    @property
    def count(self) -> int:
        return len(self._points)
