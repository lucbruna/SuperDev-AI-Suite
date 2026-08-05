"""LinkedIn Upload — post validation and orchestration (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_MAX_TEXT_LENGTH = 3000
_MAX_IMAGE_COUNT = 20
_SUPPORTED_MEDIA = {"image/jpeg", "image/png", "video/mp4"}


class LinkedInUpload:
    """Validate and orchestrate posts to LinkedIn."""

    def validate(self, *, text: str = "", media_count: int = 0, media_type: str = "") -> dict:
        """Check a post against LinkedIn content constraints."""
        issues = []
        if len(text) > _MAX_TEXT_LENGTH:
            issues.append(f"Text exceeds the {_MAX_TEXT_LENGTH} character limit.")
        if media_count > _MAX_IMAGE_COUNT:
            issues.append(f"Too many media items — maximum is {_MAX_IMAGE_COUNT}.")
        if media_type and media_type.lower() not in _SUPPORTED_MEDIA:
            issues.append(f"Unsupported media type '{media_type}'.")
        return {"valid": not issues, "issues": issues}

    def post(self, *, text: str, visibility: str = "public") -> dict:
        """Publish a post (simulated without credentials)."""
        return {
            "success": True,
            "simulated": True,
            "post_id": f"li_post_{len(text)}",
            "visibility": visibility,
            "status": "posted",
        }

    def stats(self) -> dict[str, float]:
        return {"max_text_length": _MAX_TEXT_LENGTH, "max_image_count": _MAX_IMAGE_COUNT}


_UPLOAD: LinkedInUpload | None = None


def get_linkedin_upload() -> LinkedInUpload:
    """Get the module-level singleton LinkedIn uploader."""
    global _UPLOAD
    if _UPLOAD is None:
        _UPLOAD = LinkedInUpload()
    return _UPLOAD
