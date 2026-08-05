"""X Upload — post validation and orchestration (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_MAX_TEXT_LENGTH = 280
_MAX_IMAGE_COUNT = 4
_MAX_VIDEO_SIZE_MB = 512


class XUpload:
    """Validate and orchestrate posts to X (Twitter)."""

    def validate(self, *, text: str = "", media_count: int = 0, video_size_mb: float = 0.0) -> dict:
        """Check a post against X content constraints."""
        issues = []
        if len(text) > _MAX_TEXT_LENGTH:
            issues.append(f"Text exceeds the {_MAX_TEXT_LENGTH} character limit.")
        if media_count > _MAX_IMAGE_COUNT:
            issues.append(f"Too many media items — maximum is {_MAX_IMAGE_COUNT}.")
        if video_size_mb > _MAX_VIDEO_SIZE_MB:
            issues.append(f"Video exceeds the {_MAX_VIDEO_SIZE_MB} MB upload limit.")
        return {"valid": not issues, "issues": issues}

    def post(self, *, text: str) -> dict:
        """Publish a post (simulated without credentials)."""
        return {
            "success": True,
            "simulated": True,
            "post_id": f"x_post_{len(text)}",
            "status": "posted",
        }

    def thread(self, *, texts: list[str]) -> dict:
        """Publish a thread of posts (simulated)."""
        post_ids = [f"x_post_{len(t)}" for t in texts]
        return {"success": True, "simulated": True, "post_ids": post_ids, "count": len(post_ids)}

    def stats(self) -> dict[str, float]:
        return {"max_text_length": _MAX_TEXT_LENGTH, "max_image_count": _MAX_IMAGE_COUNT, "max_video_size_mb": _MAX_VIDEO_SIZE_MB}


_UPLOAD: XUpload | None = None


def get_x_upload() -> XUpload:
    """Get the module-level singleton X uploader."""
    global _UPLOAD
    if _UPLOAD is None:
        _UPLOAD = XUpload()
    return _UPLOAD
