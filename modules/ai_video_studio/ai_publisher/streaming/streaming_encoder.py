"""Streaming Encoder — encoder presets and configuration (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_PRESETS = {
    "fast": {"codec": "h264", "preset": "veryfast", "bitrate_mbps": 4.5, "note": "Best for low-end machines"},
    "balanced": {"codec": "h264", "preset": "faster", "bitrate_mbps": 6.0, "note": "Good quality/speed trade-off"},
    "quality": {"codec": "h265", "preset": "medium", "bitrate_mbps": 6.0, "note": "Best quality, needs more CPU"},
}


class StreamingEncoder:
    """Describe and select encoder presets for live streaming."""

    def presets(self) -> dict:
        return _PRESETS

    def select(self, *, preset: str = "balanced") -> dict:
        """Return the encoder configuration for a named preset."""
        return _PRESETS.get(preset, _PRESETS["balanced"])

    def suggest(self, *, cpu_cores: int = 4) -> dict:
        """Suggest a preset based on CPU capacity."""
        if cpu_cores <= 2:
            return {"suggested": "fast", **self.select(preset="fast")}
        if cpu_cores >= 8:
            return {"suggested": "quality", **self.select(preset="quality")}
        return {"suggested": "balanced", **self.select(preset="balanced")}

    def stats(self) -> dict[str, int]:
        return {"presets": len(_PRESETS)}


_ENCODER: StreamingEncoder | None = None


def get_streaming_encoder() -> StreamingEncoder:
    """Get the module-level singleton streaming encoder."""
    global _ENCODER
    if _ENCODER is None:
        _ENCODER = StreamingEncoder()
    return _ENCODER
