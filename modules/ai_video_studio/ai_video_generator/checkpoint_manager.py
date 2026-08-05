"""Checkpoint manager — save and restore generation progress."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class CheckpointManager:
    """Persists intermediate generation state so long jobs can resume."""

    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir or Path.cwd() / "checkpoints")

    def _ensure_dir(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, job_id: str, state: dict[str, Any]) -> Path:
        self._ensure_dir()
        payload = {"saved_at": time.time(), **state}
        path = self.base_dir / f"{job_id}.json"
        path.write_text(json.dumps(payload, default=str), encoding="utf-8")
        return path

    def load(self, job_id: str) -> dict[str, Any] | None:
        path = self.base_dir / f"{job_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def delete(self, job_id: str) -> bool:
        path = self.base_dir / f"{job_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    def list_checkpoints(self) -> list[str]:
        return [p.stem for p in self.base_dir.glob("*.json")]


_checkpoint_manager: CheckpointManager | None = None


def get_checkpoint_manager() -> CheckpointManager:
    global _checkpoint_manager
    if _checkpoint_manager is None:
        _checkpoint_manager = CheckpointManager()
    return _checkpoint_manager
