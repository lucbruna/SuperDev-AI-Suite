"""Centralized path management for the video studio.

All filesystem paths flow through here so that tests can monkeypatch
a single location instead of hunting through 50 modules.
"""
from __future__ import annotations
from pathlib import Path
from functools import lru_cache
from modules.ai_video_studio.core.settings import get_settings


class VideoStudioPaths:
    """Provides validated, lazily-created directory paths."""

    def __init__(self) -> None:
        s = get_settings()
        self._storage = s.storage.local_path
        self._temp = s.storage.temp_path
        self._export = s.storage.export_path
        self._asset = s.storage.asset_path
        self._render_temp = s.render.temp_render_path

    @property
    def storage(self) -> Path:
        self._storage.mkdir(parents=True, exist_ok=True)
        return self._storage

    @property
    def temp(self) -> Path:
        self._temp.mkdir(parents=True, exist_ok=True)
        return self._temp

    @property
    def export(self) -> Path:
        self._export.mkdir(parents=True, exist_ok=True)
        return self._export

    @property
    def assets(self) -> Path:
        self._asset.mkdir(parents=True, exist_ok=True)
        return self._asset

    @property
    def render_temp(self) -> Path:
        self._render_temp.mkdir(parents=True, exist_ok=True)
        return self._render_temp

    # ── Convenience helpers ───────────────────────────────────────
    def project_dir(self, project_id: str) -> Path:
        d = self.storage / "projects" / project_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def asset_dir(self, project_id: str) -> Path:
        d = self.project_dir(project_id) / "assets"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def export_dir(self, project_id: str) -> Path:
        d = self.export / project_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def thumbnail_path(self, project_id: str, filename: str = "thumb.jpg") -> Path:
        return self.project_dir(project_id) / "thumbnails" / filename

    def render_output(self, project_id: str, filename: str = "output.mp4") -> Path:
        d = self.project_dir(project_id) / "renders"
        d.mkdir(parents=True, exist_ok=True)
        return d / filename

    def temp_file(self, name: str) -> Path:
        return self.temp / name

    def clean_temp(self) -> int:
        """Delete all files in temp directory. Returns count deleted."""
        count = 0
        if self.temp.exists():
            for f in self.temp.iterdir():
                if f.is_file():
                    f.unlink()
                    count += 1
        return count

    def disk_usage(self) -> dict[str, float]:
        """Return disk usage in MB for key directories."""
        def _usage(p: Path) -> float:
            total = 0
            if p.exists():
                for f in p.rglob("*"):
                    if f.is_file():
                        total += f.stat().st_size
            return total / (1024 * 1024)
        return {
            "storage_mb": _usage(self.storage),
            "temp_mb": _usage(self.temp),
            "export_mb": _usage(self.export),
        }


@lru_cache
def get_paths() -> VideoStudioPaths:
    """Cached singleton for path manager."""
    return VideoStudioPaths()