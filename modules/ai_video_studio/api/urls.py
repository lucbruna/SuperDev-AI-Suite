"""URL helpers for the video studio API."""
from __future__ import annotations

from urllib.parse import quote


DOWNLOAD_PREFIX = "/api/v1/video-studio/downloads"


def to_download_url(output_path: str) -> str | None:
    """Convert a path under the canonical downloads tree to a safe URL.

    The marker must be a complete path component (not an arbitrary substring),
    and traversal components are rejected before URL encoding. This keeps
    generated filenames with spaces or non-ASCII characters usable by browsers.
    """
    if not isinstance(output_path, str) or not output_path:
        return None

    normalized = output_path.replace("\\", "/")
    parts = normalized.split("/")
    # Require the canonical modules/downloads directory shape. A random
    # directory named "downloads" elsewhere on disk is not an export source.
    marker_index = next(
        (
            index
            for index in range(len(parts) - 1, 0, -1)
            if parts[index] == "downloads" and parts[index - 1] == "modules"
        ),
        None,
    )
    if marker_index is None:
        return None

    relative_parts = parts[marker_index + 1 :]
    if (
        len(relative_parts) < 2
        or any(part in {"", ".", ".."} for part in relative_parts)
    ):
        return None

    encoded = "/".join(quote(part, safe="") for part in relative_parts)
    return f"{DOWNLOAD_PREFIX}/{encoded}"
