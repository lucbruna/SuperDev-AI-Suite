"""Cloud Upload — upload validation and orchestration (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_MAX_SINGLE_SIZE_MB = 5120
_MAX_OBJECT_COUNT = 10_000


class CloudUpload:
    """Validate and orchestrate uploads to cloud storage."""

    def validate(self, *, size_mb: float = 0.0, content_type: str = "", chunked: bool = False) -> dict:
        """Check a file against cloud upload constraints."""
        issues = []
        if size_mb > _MAX_SINGLE_SIZE_MB:
            issues.append(f"File exceeds the {_MAX_SINGLE_SIZE_MB} MB single-upload limit — use chunked upload.")
        if content_type and not content_type.startswith(("video/", "image/", "audio/", "text/", "application/")):
            issues.append(f"Unexpected content type '{content_type}'.")
        return {"valid": not issues, "issues": issues, "recommend_chunked": size_mb > 1000.0 or chunked}

    def upload(self, *, key: str = "", size_mb: float = 0.0) -> dict:
        """Upload a file (simulated)."""
        return {
            "success": True,
            "simulated": True,
            "key": key or f"uploads/object_{int(size_mb)}",
            "size_mb": size_mb,
            "status": "uploaded",
        }

    def stats(self) -> dict[str, float]:
        return {"max_single_size_mb": _MAX_SINGLE_SIZE_MB, "max_object_count": _MAX_OBJECT_COUNT}


_UPLOAD: CloudUpload | None = None


def get_cloud_upload() -> CloudUpload:
    """Get the module-level singleton cloud uploader."""
    global _UPLOAD
    if _UPLOAD is None:
        _UPLOAD = CloudUpload()
    return _UPLOAD
