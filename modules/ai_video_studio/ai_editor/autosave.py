"""Autosave manager — periodic saving of the open project.

Writes ``<id>.autosave.json`` every ``interval_seconds`` while dirty, and on
``save_now()``. Uses a daemon timer so the editor thread is never blocked.
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.autosave")


class AutosaveManager:
    def __init__(self, manager: Any, interval_seconds: float = 30.0) -> None:
        self.manager = manager
        self.interval = max(1.0, float(interval_seconds))
        self.is_dirty = False
        self._timer: threading.Timer | None = None
        self._dir = Path(getattr(manager, "projects", None).directory if getattr(manager, "projects", None) else "./editor_projects")
        self._dir.mkdir(parents=True, exist_ok=True)

    def mark_dirty(self) -> None:
        self.is_dirty = True
        self._schedule()

    def mark_clean(self) -> None:
        self.is_dirty = False

    def save_now(self) -> str | None:
        """Write an autosave for the current project; returns the path or None."""
        current = getattr(self.manager, "_current", None)
        if current is None or not current.get("id"):
            return None
        project_id = current["id"]
        path = self._dir / f"{project_id}.autosave.json"
        payload = {
            "project_id": project_id,
            "saved_at": time.time(),
            "timeline": self.manager.engine.timeline.to_dict(),
        }
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp, path)
        self.is_dirty = False
        logger.info("autosaved %s", path.name)
        return str(path)

    def _schedule(self) -> None:
        if self._timer and self._timer.is_alive():
            return
        timer = threading.Timer(self.interval, self._tick)
        timer.daemon = True
        self._timer = timer
        timer.start()

    def _tick(self) -> None:
        try:
            if self.is_dirty:
                self.save_now()
        finally:
            self._timer = None
            if self.is_dirty:
                self._schedule()

    def shutdown(self) -> None:
        if self._timer:
            self._timer.cancel()
        if self.is_dirty:
            self.save_now()
