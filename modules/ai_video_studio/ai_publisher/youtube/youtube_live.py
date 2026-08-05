"""YouTube Live — live stream scheduling and metadata (Volume 7)."""
from __future__ import annotations

import logging
import time
import uuid

logger = logging.getLogger(__name__)

_STATES = ("draft", "scheduled", "live", "ended")


class YoutubeLive:
    """Manage live stream lifecycle and broadcast metadata."""

    def __init__(self) -> None:
        self._streams: dict[str, dict] = {}

    def create_broadcast(self, *, title: str, start_time: float | None = None, description: str = "") -> dict:
        """Create a live broadcast entry."""
        broadcast_id = uuid.uuid4().hex[:12]
        stream = {
            "broadcast_id": broadcast_id,
            "title": title,
            "description": description,
            "state": "draft",
            "start_time": start_time,
            "created_at": time.time(),
        }
        self._streams[broadcast_id] = stream
        return stream

    def set_state(self, broadcast_id: str, state: str) -> dict:
        """Transition a broadcast between draft → scheduled → live → ended."""
        stream = self._streams.get(broadcast_id)
        if not stream:
            return {"success": False, "error": "Unknown broadcast"}
        if state not in _STATES:
            return {"success": False, "error": f"Invalid state '{state}'"}
        stream["state"] = state
        if state == "live":
            stream["started_at"] = time.time()
        elif state == "ended":
            stream["ended_at"] = time.time()
        return {"success": True, "stream": stream}

    def list(self) -> list[dict]:
        return sorted(self._streams.values(), key=lambda s: s["created_at"], reverse=True)

    def stats(self) -> dict[str, int]:
        return {"streams": len(self._streams)}


_LIVE: YoutubeLive | None = None


def get_youtube_live() -> YoutubeLive:
    """Get the module-level singleton live manager."""
    global _LIVE
    if _LIVE is None:
        _LIVE = YoutubeLive()
    return _LIVE
