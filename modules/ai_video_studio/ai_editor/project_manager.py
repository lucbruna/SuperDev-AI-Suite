"""Project manager — project CRUD with real JSON persistence.

Projects are stored as ``<name>.sdevproj.json`` files under a configurable
projects directory (default ``./editor_projects``). Every mutation writes an
atomic file (tmp + rename) so a crash never corrupts the last good copy.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import NotFoundError, ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.project")


class ProjectManager:
    """Create/open/save/list projects backed by JSON files on disk."""

    def __init__(self, directory: str | Path = "./editor_projects") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, Any]] = {}

    def _path(self, project_id: str) -> Path:
        return self.directory / f"{project_id}.sdevproj.json"

    def create_project(self, name: str, *, fps: int = 24, width: int = 1920, height: int = 1080) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValidationError("Project name is required", field="name")
        project_id = uuid.uuid4().hex[:12]
        project: dict[str, Any] = {
            "id": project_id,
            "name": name.strip(),
            "fps": int(fps),
            "width": int(width),
            "height": int(height),
            "timeline": {"tracks": {}, "clips": [], "markers": [], "subtitles": []},
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        self._write(project)
        self._cache[project_id] = project
        logger.info("Created project %s (%s)", project_id, name)
        return project

    def load_project(self, project_id: str) -> dict[str, Any]:
        if project_id in self._cache:
            return dict(self._cache[project_id])
        path = self._path(project_id)
        if not path.exists():
            raise NotFoundError("Project", project_id)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise ValidationError(f"Project file is corrupt: {exc}", field="project") from exc
        self._cache[project_id] = data
        return dict(data)

    def save_project(self, project: dict[str, Any]) -> dict[str, Any]:
        project_id = project.get("id")
        if not project_id:
            raise ValidationError("Project has no id", field="id")
        project["updated_at"] = time.time()
        self._write(project)
        self._cache[project_id] = dict(project)
        return project

    def list_projects(self) -> list[dict[str, Any]]:
        projects = []
        for path in sorted(self.directory.glob("*.sdevproj.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                projects.append({"id": data.get("id", path.stem), "name": data.get("name", path.stem)})
            except (json.JSONDecodeError, OSError):
                continue
        return projects

    def delete_project(self, project_id: str) -> bool:
        self._cache.pop(project_id, None)
        path = self._path(project_id)
        if path.exists():
            path.unlink()
            return True
        return False

    def _write(self, project: dict[str, Any]) -> None:
        tmp = self._path(project["id"]).with_suffix(".tmp")
        tmp.write_text(json.dumps(project, indent=2), encoding="utf-8")
        os.replace(tmp, self._path(project["id"]))


_project_manager: ProjectManager | None = None


def get_project_manager(directory: str | Path = "./editor_projects") -> ProjectManager:
    """Cached project manager."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager(directory)
    return _project_manager
