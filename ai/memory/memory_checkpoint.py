from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class MemoryCheckpoint:
    """Checkpoint mechanism for saving and loading execution state."""

    def __init__(self, checkpoint_dir: str | Path | None = None):
        self._checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else None
        self._checkpoints: dict[str, dict[str, Any]] = {}

    @property
    def checkpoint_dir(self) -> Path | None:
        return self._checkpoint_dir

    def save(self, checkpoint_id: str, state: dict[str, Any]) -> str:
        key = f"{checkpoint_id}_{time.time()}"
        self._checkpoints[key] = {
            "state": state,
            "timestamp": time.time(),
            "checkpoint_id": checkpoint_id,
        }
        if self._checkpoint_dir:
            self._write_to_disk(key)
        return key

    def load(self, checkpoint_id: str) -> dict[str, Any] | None:
        checkpoint = self._checkpoints.get(checkpoint_id)
        if checkpoint:
            return dict(checkpoint.get("state", {}))
        if self._checkpoint_dir:
            return self._read_from_disk(checkpoint_id)
        return None

    def load_latest(self, prefix: str = "") -> dict[str, Any] | None:
        candidates = [(key, cp) for key, cp in self._checkpoints.items() if key.startswith(prefix)]
        if not candidates:
            return None
        candidates.sort(key=lambda x: x[1]["timestamp"], reverse=True)
        return dict(candidates[0][1].get("state", {}))

    def list_checkpoints(self, prefix: str = "") -> list[dict[str, Any]]:
        results = [
            {
                "key": key,
                "checkpoint_id": cp["checkpoint_id"],
                "timestamp": cp["timestamp"],
            }
            for key, cp in self._checkpoints.items()
            if key.startswith(prefix)
        ]
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results

    def delete(self, checkpoint_id: str) -> bool:
        if checkpoint_id in self._checkpoints:
            del self._checkpoints[checkpoint_id]
            if self._checkpoint_dir:
                self._delete_from_disk(checkpoint_id)
            return True
        return False

    def clear(self) -> None:
        self._checkpoints.clear()

    def _write_to_disk(self, key: str) -> None:
        if not self._checkpoint_dir:
            return
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
        path = self._checkpoint_dir / f"{key}.json"
        path.write_text(json.dumps(self._checkpoints[key], indent=2))

    def _read_from_disk(self, checkpoint_id: str) -> dict[str, Any] | None:
        if not self._checkpoint_dir:
            return None
        for path in self._checkpoint_dir.glob("*.json"):
            if checkpoint_id in path.stem:
                data = json.loads(path.read_text())
                return dict(data.get("state", {}))
        return None

    def _delete_from_disk(self, checkpoint_id: str) -> None:
        if not self._checkpoint_dir:
            return
        for path in self._checkpoint_dir.glob(f"{checkpoint_id}*.json"):
            path.unlink(missing_ok=True)

    def size(self) -> int:
        return len(self._checkpoints)
