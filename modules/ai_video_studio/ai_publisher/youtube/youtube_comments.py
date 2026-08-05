"""YouTube Comments — comment management and moderation (Volume 7)."""
from __future__ import annotations

import logging
import time
import uuid

logger = logging.getLogger(__name__)

_BLACKLIST = ["spam", "click here", "free money", "sorteio falso", "compre agora"]


class YoutubeComments:
    """Moderate and manage YouTube comments."""

    def __init__(self) -> None:
        self._comments: dict[str, dict] = {}

    def ingest(self, *, video_id: str, author: str, text: str) -> dict:
        """Add a comment with an initial moderation verdict."""
        comment_id = uuid.uuid4().hex[:12]
        lowered = text.lower()
        verdict = "blocked" if any(b in lowered for b in _BLACKLIST) else "approved"
        comment = {
            "id": comment_id,
            "video_id": video_id,
            "author": author,
            "text": text,
            "verdict": verdict,
            "created_at": time.time(),
        }
        self._comments[comment_id] = comment
        return comment

    def list(self, *, video_id: str | None = None) -> list[dict]:
        comments = list(self._comments.values())
        if video_id:
            comments = [c for c in comments if c["video_id"] == video_id]
        return sorted(comments, key=lambda c: c["created_at"], reverse=True)

    def set_verdict(self, comment_id: str, verdict: str) -> bool:
        comment = self._comments.get(comment_id)
        if not comment:
            return False
        comment["verdict"] = verdict
        return True

    def stats(self) -> dict[str, int]:
        return {"comments": len(self._comments)}


_COMMENTS: YoutubeComments | None = None


def get_youtube_comments() -> YoutubeComments:
    """Get the module-level singleton comment manager."""
    global _COMMENTS
    if _COMMENTS is None:
        _COMMENTS = YoutubeComments()
    return _COMMENTS
