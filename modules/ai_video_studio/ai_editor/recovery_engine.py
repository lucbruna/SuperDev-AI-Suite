"""Recovery engine — crash recovery from autosave files.

Scans the projects directory for ``*.autosave.json`` files, picks the most
recent valid one and returns the reconstructed project (timeline + id + name
resolved from the main project file when available).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.recovery")


class RecoveryEngine:
    def __init__(self, projects_dir: str | Path) -> None:
        self.dir = Path(projects_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def autosaves(self) -> list[dict[str, Any]]:
        """All readable autosaves sorted by saved_at (oldest first)."""
        found: list[dict[str, Any]] = []
        for path in self.dir.glob("*.autosave.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                found.append({"path": str(path), **data})
            except (json.JSONDecodeError, OSError):
                continue
        return sorted(found, key=lambda d: d.get("saved_at", 0))

    def recover_latest(self) -> dict[str, Any] | None:
        """Reconstruct the project from the newest valid autosave (or None)."""
        autosaves = self.autosaves()
        if not autosaves:
            return None
        latest = autosaves[-1]
        project_id = latest.get("project_id")
        name = project_id or "recovered"
        main = self.dir / f"{project_id}.sdevproj.json" if project_id else None
        if main and main.exists():
            try:
                name = json.loads(main.read_text(encoding="utf-8")).get("name", name)
            except (json.JSONDecodeError, OSError):
                pass
        logger.info("recovering project '%s' from %s", name, Path(latest["path"]).name)
        return {
            "id": project_id,
            "name": name,
            "recovered_at": time.time(),
            "timeline": latest.get("timeline", {}),
        }

    def discard_autosaves(self, project_id: str) -> int:
        removed = 0
        for path in self.dir.glob(f"{project_id}.autosave.json"):
            path.unlink(missing_ok=True)
            removed += 1
        return removed
