"""Editor manager — high-level facade for the professional editor.

Binds a project (persisted by :class:`ProjectManager`) to an
:class:`EditorEngine` and provides session-level operations: open/save, add
media, edit, autosave, recover and render. This is the API a UI/backend would
consume.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger
from modules.ai_video_studio.ai_editor.editor_engine import EditorEngine
from modules.ai_video_studio.ai_editor.autosave import AutosaveManager
from modules.ai_video_studio.ai_editor.recovery_engine import RecoveryEngine
from modules.ai_video_studio.ai_editor.project_manager import ProjectManager

logger = make_logger("editor.manager")


class EditorManager:
    def __init__(self, projects_dir: str | Path = "./editor_projects") -> None:
        self.projects = ProjectManager(projects_dir)
        self.engine = EditorEngine()
        self.autosave = AutosaveManager(self)
        self.recovery = RecoveryEngine(projects_dir)
        self._current: dict[str, Any] | None = None

    # ── Session ──────────────────────────────────────────────────
    def new_project(self, name: str, *, fps: int = 24, width: int = 1920, height: int = 1080) -> dict[str, Any]:
        project = self.projects.create_project(name, fps=fps, width=width, height=height)
        self.engine.timeline.fps = fps
        self.engine.timeline.load_dict(project.get("timeline", {}))
        self._current = project
        self.autosave.mark_dirty()
        return project

    def open_project(self, project_id: str) -> dict[str, Any]:
        project = self.projects.load_project(project_id)
        self.engine.timeline.load_dict(project.get("timeline", {}))
        self._current = project
        return project

    def save(self) -> dict[str, Any]:
        if self._current is None:
            raise ValidationError("No project open", field="project")
        self._current["timeline"] = self.engine.timeline.to_dict()
        self._current = self.projects.save_project(self._current)
        self.autosave.mark_clean()
        return self._current

    def recover_last(self) -> dict[str, Any] | None:
        recovered = self.recovery.recover_latest()
        if recovered:
            self.engine.timeline.load_dict(recovered.get("timeline", {}))
            self._current = recovered
        return recovered

    # ── Media / edit passthrough ─────────────────────────────────
    def add_media_clip(self, source: str, start: float, end: float, track: str = "video", **props: Any) -> dict[str, Any]:
        clip = self.engine.add_clip({"source": source, "start": start, "end": end, **props}, track=track)
        self.autosave.mark_dirty()
        return clip

    def render(self, output_path: str, *, fps: int | None = None, width: int | None = None, height: int | None = None) -> dict[str, Any]:
        result = self.engine.render(
            output_path,
            fps=fps or self._current.get("fps", 24) if self._current else 24,
            width=width or (self._current.get("width") if self._current else None),
            height=height or (self._current.get("height") if self._current else None),
        )
        self.autosave.mark_dirty()
        return result

    def snapshot_stats(self) -> dict[str, Any]:
        stats = self.engine.stats()
        stats["autosave_dirty"] = self.autosave.is_dirty
        return stats
