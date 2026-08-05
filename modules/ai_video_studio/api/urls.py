"""URL helpers for the video studio API."""
from __future__ import annotations

DOWNLOAD_PREFIX = "/api/v1/video-studio/downloads"


def to_download_url(output_path: str) -> str | None:
    """Convert an absolute output path into a relative download URL.

    Only paths inside the canonical ``modules/downloads/`` tree map to a
    downloadable URL; everything else returns ``None``.
    """
    try:
        rel = output_path.replace("\\", "/")
        marker = "downloads/"
        if marker in rel:
            return f"{DOWNLOAD_PREFIX}/{rel.split(marker, 1)[1]}"
    except Exception:  # noqa: BLE001 — best effort URL conversion
        return None
    return None
