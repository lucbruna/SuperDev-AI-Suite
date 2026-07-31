from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class MemorySnapshot:
    """Point-in-time snapshot of memory state."""

    def __init__(self, snapshot_dir: str | Path | None = None):
        self._snapshot_dir = Path(snapshot_dir) if snapshot_dir else None
        self._snapshots: dict[str, dict[str, Any]] = {}

    def create(self, snapshot_id: str, state: dict[str, Any]) -> str:
        key = f"{snapshot_id}_{int(time.time())}"
        self._snapshots[key] = {
            "state": dict(state),
            "timestamp": time.time(),
            "snapshot_id": snapshot_id,
        }
        if self._snapshot_dir:
            self._write_to_disk(key)
        return key

    def load(self, snapshot_id: str) -> dict[str, Any] | None:
        snapshot = self._snapshots.get(snapshot_id)
        if snapshot:
            return dict(snapshot.get("state", {}))
        if self._snapshot_dir:
            return self._read_from_disk(snapshot_id)
        return None

    def list_snapshots(self, prefix: str = "") -> list[dict[str, Any]]:
        results = [
            {"key": k, "snapshot_id": v["snapshot_id"], "timestamp": v["timestamp"]}
            for k, v in self._snapshots.items()
            if k.startswith(prefix)
        ]
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results

    def delete(self, snapshot_id: str) -> bool:
        if snapshot_id in self._snapshots:
            del self._snapshots[snapshot_id]
            if self._snapshot_dir:
                self._delete_from_disk(snapshot_id)
            return True
        return False

    def load_latest(self, prefix: str = "") -> dict[str, Any] | None:
        candidates = [(key, snap) for key, snap in self._snapshots.items() if key.startswith(prefix)]
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[1]["timestamp"], reverse=True)
        return dict(candidates[0][1].get("state", {}))

    def clear(self) -> None:
        self._snapshots.clear()

    def _write_to_disk(self, key: str) -> None:
        if not self._snapshot_dir:
            return
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)
        path = self._snapshot_dir / f"{key}.snap"
        path.write_text(json.dumps(self._snapshots[key], indent=2))

    def _read_from_disk(self, snapshot_id: str) -> dict[str, Any] | None:
        if not self._snapshot_dir:
            return None
        for path in self._snapshot_dir.glob("*.snap"):
            if snapshot_id in path.stem:
                data = json.loads(path.read_text())
                return dict(data.get("state", {}))
        return None

    def _delete_from_disk(self, snapshot_id: str) -> None:
        if not self._snapshot_dir:
            return
        for path in self._snapshot_dir.glob(f"{snapshot_id}*.snap"):
            path.unlink(missing_ok=True)

    @property
    def count(self) -> int:
        return len(self._snapshots)
