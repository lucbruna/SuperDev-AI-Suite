"""YouTube Upload — video upload validation and orchestration (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# YouTube upload limits (public uploads).
_MAX_SIZE_MB = 128 * 1024  # 128 GB
_MAX_DURATION_MINUTES = 12 * 60


class YoutubeUpload:
    """Validate and orchestrate video uploads to YouTube."""

    def validate(self, *, path: str = "", size_mb: float = 0.0, duration_minutes: float = 0.0) -> dict:
        """Check a file against YouTube upload constraints."""
        issues = []
        if path and not size_mb:
            issues.append("File size unknown — supply size_mb.")
        if size_mb > _MAX_SIZE_MB:
            issues.append(f"File exceeds the {_MAX_SIZE_MB:,} MB upload limit.")
        if duration_minutes > _MAX_DURATION_MINUTES:
            issues.append(f"Duration exceeds the {_MAX_DURATION_MINUTES} minute limit.")
        valid = not issues
        return {"valid": valid, "issues": issues, "size_mb": size_mb}

    def upload(self, *, title: str, path: str, description: str = "") -> dict:
        """Upload a video (simulated without credentials)."""
        validation = self.validate(path=path)
        if not validation["valid"]:
            return {"success": False, "errors": validation["issues"]}
        return {
            "success": True,
            "simulated": True,
            "video_id": f"vid_upload_{len(title)}{len(path)}",
            "title": title,
            "status": "processing",
        }

    def stats(self) -> dict[str, float]:
        return {"max_size_mb": _MAX_SIZE_MB, "max_duration_minutes": _MAX_DURATION_MINUTES}


_UPLOAD: YoutubeUpload | None = None


def get_youtube_upload() -> YoutubeUpload:
    """Get the module-level singleton YouTube uploader."""
    global _UPLOAD
    if _UPLOAD is None:
        _UPLOAD = YoutubeUpload()
    return _UPLOAD
