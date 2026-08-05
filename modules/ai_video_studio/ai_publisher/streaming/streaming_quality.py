"""Streaming Quality — resolution, bitrate, and stability checks (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_BITRATE_TABLE = {"720p": 4.5, "1080p": 6.0, "1440p": 9.0, "4k": 13.5}  # Mbps


class StreamingQuality:
    """Validate stream quality settings and health."""

    def recommend_bitrate(self, *, resolution: str = "1080p") -> dict:
        """Return recommended upload bitrate for a resolution."""
        bitrate = _BITRATE_TABLE.get(resolution, 6.0)
        return {"resolution": resolution, "bitrate_mbps": bitrate, "buffer_recommended": bitrate * 0.15}

    def check(self, *, bitrate_mbps: float = 0.0, framerate: int = 30, dropped_frames: int = 0, total_frames: int = 0) -> dict:
        """Evaluate stream stability signals."""
        issues = []
        if bitrate_mbps < 4.5:
            issues.append("Bitrate is below the minimum recommended for 720p.")
        if framerate not in (24, 30, 60):
            issues.append("Use a standard framerate (24, 30, or 60 fps).")
        if total_frames and dropped_frames / total_frames > 0.05:
            issues.append("Dropped frame rate exceeds 5%.")
        return {"healthy": not issues, "issues": issues}

    def stats(self) -> dict[str, int]:
        return {"resolutions": len(_BITRATE_TABLE)}


_QUALITY: StreamingQuality | None = None


def get_streaming_quality() -> StreamingQuality:
    """Get the module-level singleton streaming quality checker."""
    global _QUALITY
    if _QUALITY is None:
        _QUALITY = StreamingQuality()
    return _QUALITY
