"""YouTube Playlist — playlist management helpers (Volume 7)."""
from __future__ import annotations

import logging
import time
import uuid

logger = logging.getLogger(__name__)


class YoutubePlaylist:
    """Create playlists and add/remove videos from them."""

    def __init__(self) -> None:
        self._playlists: dict[str, dict] = {}

    def create(self, *, title: str, description: str = "") -> dict:
        playlist_id = uuid.uuid4().hex[:12]
        playlist = {
            "playlist_id": playlist_id,
            "title": title,
            "description": description,
            "video_ids": [],
            "created_at": time.time(),
        }
        self._playlists[playlist_id] = playlist
        return playlist

    def add_video(self, playlist_id: str, video_id: str) -> dict:
        playlist = self._playlists.get(playlist_id)
        if not playlist:
            return {"success": False, "error": "Unknown playlist"}
        if video_id not in playlist["video_ids"]:
            playlist["video_ids"].append(video_id)
        return {"success": True, "playlist_id": playlist_id, "count": len(playlist["video_ids"])}

    def remove_video(self, playlist_id: str, video_id: str) -> dict:
        playlist = self._playlists.get(playlist_id)
        if not playlist:
            return {"success": False, "error": "Unknown playlist"}
        if video_id in playlist["video_ids"]:
            playlist["video_ids"].remove(video_id)
        return {"success": True, "count": len(playlist["video_ids"])}

    def list(self) -> list[dict]:
        return list(self._playlists.values())

    def stats(self) -> dict[str, int]:
        return {"playlists": len(self._playlists)}


_PLAYLIST: YoutubePlaylist | None = None


def get_youtube_playlist() -> YoutubePlaylist:
    """Get the module-level singleton playlist manager."""
    global _PLAYLIST
    if _PLAYLIST is None:
        _PLAYLIST = YoutubePlaylist()
    return _PLAYLIST
