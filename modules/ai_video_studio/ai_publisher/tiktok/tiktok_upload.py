"""TikTok Upload — upload validation and orchestration (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_MAX_SIZE_MB = 2048
_MAX_DURATION_SECONDS = 600
_SUPPORTED_FORMATS = {"mp4", "mov", "webm", "avi"}


class TikTokUpload:
    """Validate and orchestrate video uploads to TikTok."""

    def validate(self, *, size_mb: float = 0.0, duration_seconds: float = 0.0, file_format: str = "") -> dict:
        """Check a file against TikTok upload constraints."""
        issues = []
        if size_mb > _MAX_SIZE_MB:
            issues.append(f"File exceeds the {_MAX_SIZE_MB} MB upload limit.")
        if duration_seconds > _MAX_DURATION_SECONDS:
            issues.append(f"Duration exceeds the {_MAX_DURATION_SECONDS} second limit.")
        if file_format and file_format.lower().lstrip(".") not in _SUPPORTED_FORMATS:
            issues.append(f"Unsupported format '{file_format}' — use MP4, MOV, WEBM or AVI.")
        return {"valid": not issues, "issues": issues}

    def upload(self, *, title: str, path: str, description: str = "") -> dict:
        """Upload a video (simulated without credentials)."""
        return {
            "success": True,
            "simulated": True,
            "post_id": f"tt_upload_{len(title)}{len(path)}",
            "title": title,
            "status": "posted",
        }

    def stats(self) -> dict[str, float]:
        return {"max_size_mb": _MAX_SIZE_MB, "max_duration_seconds": _MAX_DURATION_SECONDS}


_UPLOAD: TikTokUpload | None = None


def get_tiktok_upload() -> TikTokUpload:
    """Get the module-level singleton TikTok uploader."""
    global _UPLOAD
    if _UPLOAD is None:
        _UPLOAD = TikTokUpload()
    return _UPLOAD
