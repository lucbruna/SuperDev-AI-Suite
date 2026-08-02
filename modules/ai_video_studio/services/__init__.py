"""Services package — business logic layer for the video studio.

Services encapsulate domain logic between the API routes and
the database / render / pipeline layers.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.settings import get_settings
from modules.ai_video_studio.core.constants import RESOLUTION_PRESETS

logger = logging.getLogger(__name__)


def _get_paths():
    from modules.ai_video_studio.core.paths import get_paths
    return get_paths()


class ProjectService:
    """Manages video project lifecycle: create, update, validate, archive."""

    def __init__(self) -> None:
        self.paths = _get_paths()
        self.settings = get_settings()

    def validate_project_config(self, data: dict[str, Any]) -> list[str]:
        errors = []
        if not data.get("name", "").strip():
            errors.append("Project name is required")
        if data.get("frame_rate") and data["frame_rate"] not in (1, 15, 24, 25, 30, 48, 50, 60, 120):
            errors.append(f"Unsupported frame rate: {data['frame_rate']}")
        return errors

    def create_project_directories(self, project_id: str) -> dict[str, str]:
        dirs = {
            "root": str(self.paths.project_dir(project_id)),
            "assets": str(self.paths.asset_dir(project_id)),
            "exports": str(self.paths.export_dir(project_id)),
            "renders": str(self.paths.render_output(project_id, "").rsplit("/", 1)[0]),
            "temp": str(self.paths.temp / project_id),
        }
        for d in dirs.values():
            Path(d).mkdir(parents=True, exist_ok=True)
        return dirs

    def calculate_project_stats(self, project_data: dict, scenes: list[dict]) -> dict[str, Any]:
        total_duration = sum(s.get("duration", 0) for s in scenes)
        return {
            "scene_count": len(scenes),
            "total_duration": total_duration,
            "estimated_render_time": total_duration * 0.5,
            "estimated_file_size_mb": total_duration * 2.5,
        }


class RenderService:
    """Manages render job lifecycle and FFmpeg orchestration."""

    def __init__(self) -> None:
        self.paths = _get_paths()
        self.settings = get_settings()

    def estimate_render_time(self, config: dict[str, Any]) -> float:
        resolution = config.get("output_resolution", "1920x1080")
        try:
            w, h = resolution.split("x")
            pixels = int(w) * int(h)
        except (ValueError, AttributeError):
            pixels = 1920 * 1080
        pixels_per_sec = 10_000_000
        duration = config.get("duration_seconds", 30.0)
        factor = pixels / pixels_per_sec
        return duration * factor * 1.2

    def estimate_file_size(self, duration: float, config: dict[str, Any]) -> float:
        crf = config.get("crf", 23)
        resolution = config.get("output_resolution", "1920x1080")
        try:
            w, h = resolution.split("x")
            pixels = int(w) * int(h)
        except (ValueError, AttributeError):
            pixels = 1920 * 1080
        bitrate_mbps = max(1.0, (pixels / 1000000) * (30 - crf) * 0.3)
        return (bitrate_mbps * duration) / 8

    def get_available_presets(self) -> list[dict[str, Any]]:
        return [{"name": k, "resolution": v["resolution"].value, "aspect_ratio": v["aspect_ratio"].value, "frame_rate": v["frame_rate"].value, "video_codec": v["video_codec"].value, "audio_codec": v["audio_codec"].value, "container": v["container"].value} for k, v in RESOLUTION_PRESETS.items()]


class AssetService:
    """Manages project assets: validation, metadata extraction, cleanup."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.paths = _get_paths()

    def validate_upload(self, filename: str, size_bytes: int, content_type: str) -> list[str]:
        errors = []
        max_bytes = self.settings.storage.max_upload_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            errors.append(f"File size {size_bytes / 1048576:.1f}MB exceeds limit of {self.settings.storage.max_upload_size_mb}MB")
        allowed = {"video/mp4", "video/quicktime", "video/webm", "audio/mpeg", "audio/wav", "image/jpeg", "image/png", "image/webp"}
        if content_type and content_type not in allowed:
            errors.append(f"Content type '{content_type}' is not supported")
        return errors

    def get_asset_type(self, content_type: str) -> str:
        mapping = {"video/": "video", "audio/": "audio", "image/": "image"}
        for prefix, atype in mapping.items():
            if content_type and content_type.startswith(prefix):
                return atype
        return "other"


class TimelineService:
    """Manages timeline assembly: clip ordering, duration calculations, conflicts."""

    def validate_clip_placement(self, clips: list[dict], new_clip: dict) -> list[str]:
        errors = []
        new_start = new_clip.get("start", 0)
        new_end = new_clip.get("end", 0)
        if new_end <= new_start:
            errors.append("Clip end must be after start")
        for c in clips:
            if new_start < c["end"] and new_end > c["start"]:
                errors.append(f"Overlaps with clip on scene {c.get('scene_id', '?')}")
        return errors

    def calculate_total_duration(self, clips: list[dict]) -> float:
        if not clips:
            return 0.0
        return max(c["end"] for c in clips)

    def auto_arrange(self, clips: list[dict]) -> list[dict]:
        arranged = []
        offset = 0.0
        for clip in sorted(clips, key=lambda c: c.get("order", 0)):
            duration = clip["end"] - clip["start"]
            arranged.append({**clip, "start": offset, "end": offset + duration})
            offset += duration
        return arranged


class ExportService:
    """Manages export history and platform publishing coordination."""

    def validate_export_config(self, config: dict[str, Any]) -> list[str]:
        errors = []
        fmt = config.get("output_format", "mp4")
        supported = {"mp4", "mov", "mkv", "webm", "avi", "gif"}
        if fmt not in supported:
            errors.append(f"Export format '{fmt}' not supported. Use: {', '.join(supported)}")
        return errors

    def get_platform_requirements(self, platform: str) -> dict[str, Any]:
        requirements = {
            "youtube": {"max_duration": 43200, "max_size_gb": 128, "formats": ["mp4", "mov", "avi"], "resolution": "up to 8K"},
            "tiktok": {"max_duration": 600, "max_size_gb": 4, "formats": ["mp4", "mov"], "resolution": "up to 1080p", "aspect": "9:16"},
            "instagram": {"max_duration": 3600, "max_size_gb": 4, "formats": ["mp4", "mov"], "resolution": "up to 1080p"},
            "facebook": {"max_duration": 14400, "max_size_gb": 10, "formats": ["mp4"], "resolution": "up to 1080p"},
            "linkedin": {"max_duration": 600, "max_size_gb": 5, "formats": ["mp4"], "resolution": "up to 1080p"},
        }
        return requirements.get(platform, {"max_duration": 3600, "max_size_gb": 4, "formats": ["mp4"]})
