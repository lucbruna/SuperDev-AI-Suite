"""Publisher History — records publish history entries (Volume 7)."""
from __future__ import annotations

import json
import logging
import time
import uuid

logger = logging.getLogger(__name__)


class PublisherHistory:
    """In-memory publish history with optional JSON persistence."""

    def __init__(self) -> None:
        self._entries: list[dict] = []
        self._max_entries = 500

    def add(self, *, platform: str, content_title: str, result: dict | None = None) -> dict:
        """Record one publish event."""
        entry = {
            "id": uuid.uuid4().hex[:12],
            "ts": time.time(),
            "platform": platform.lower(),
            "content_title": content_title,
            "status": (result or {}).get("status", "published"),
            "result": result or {},
        }
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]
        return entry

    def list(self, *, platform: str | None = None, limit: int = 100) -> list[dict]:
        entries = self._entries
        if platform:
            entries = [e for e in entries if e["platform"] == platform.lower()]
        return list(reversed(entries[-limit:]))

    def save(self) -> dict:
        """Persist history to JSON under the downloads dir."""
        try:
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename

            directory = get_subsystem_dir("publish")
            path = unique_filename(directory, "publish_history", "json")
            path.write_text(json.dumps(self._entries, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"saved": True, "path": str(path), "entries": len(self._entries)}
        except Exception as exc:  # noqa: BLE001
            return {"saved": False, "error": str(exc)}

    def stats(self) -> dict[str, int]:
        return {"entries": len(self._entries)}


_HISTORY: PublisherHistory | None = None


def get_publisher_history() -> PublisherHistory:
    """Get the module-level singleton history store."""
    global _HISTORY
    if _HISTORY is None:
        _HISTORY = PublisherHistory()
    return _HISTORY
