"""Streaming Go Live — start, stop, and manage live sessions (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class StreamingGoLive:
    """Orchestrate live streaming sessions."""

    def __init__(self) -> None:
        self._streams: dict[str, dict] = {}

    def start(self, *, title: str = "", encoder: str = "rtmp") -> dict:
        """Start a live session (simulated)."""
        stream_id = f"live_{len(title)}_{len(self._streams) + 1}"
        stream = {"stream_id": stream_id, "title": title or "Untitled stream", "encoder": encoder, "status": "live"}
        self._streams[stream_id] = stream
        return stream

    def stop(self, *, stream_id: str = "") -> dict:
        """Stop a live session (simulated)."""
        stream = self._streams.get(stream_id or "")
        if stream is None:
            return {"success": False, "reason": "stream not found"}
        stream["status"] = "ended"
        return {"success": True, "stream_id": stream_id, "status": "ended"}

    def list_active(self) -> list[dict]:
        return [s for s in self._streams.values() if s["status"] == "live"]

    def stats(self) -> dict[str, int]:
        return {"streams": len(self._streams), "active": len(self.list_active())}


_GO_LIVE: StreamingGoLive | None = None


def get_streaming_go_live() -> StreamingGoLive:
    """Get the module-level singleton live-stream manager."""
    global _GO_LIVE
    if _GO_LIVE is None:
        _GO_LIVE = StreamingGoLive()
    return _GO_LIVE
