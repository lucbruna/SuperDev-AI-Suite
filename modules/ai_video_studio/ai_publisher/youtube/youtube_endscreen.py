"""YouTube Endscreen — end screen element layouts (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_ELEMENT_TYPES = ("video", "playlist", "channel", "subscribe", "link")


class YoutubeEndscreen:
    """Compose YouTube end screen element configurations."""

    def build(self, *, video_id: str = "", playlist_id: str = "", channel_id: str = "", subscribe: bool = True) -> dict:
        """Build an end screen layout with available elements."""
        elements = []
        if video_id:
            elements.append({"type": "video", "video_id": video_id, "position": [0.25, 0.3], "size": [0.5, 0.5]})
        elif playlist_id:
            elements.append({"type": "playlist", "playlist_id": playlist_id, "position": [0.25, 0.3], "size": [0.5, 0.5]})
        elif channel_id:
            elements.append({"type": "channel", "channel_id": channel_id, "position": [0.25, 0.3], "size": [0.5, 0.5]})
        if subscribe:
            elements.append({"type": "subscribe", "position": [0.15, 0.7], "size": [0.2, 0.15]})
        if len(elements) < 2:
            elements.append({"type": "link", "position": [0.65, 0.7], "size": [0.2, 0.15], "url": ""})
        return {"elements": elements, "count": len(elements)}

    def validate_type(self, element_type: str) -> bool:
        return element_type in _ELEMENT_TYPES

    def stats(self) -> dict[str, int]:
        return {"element_types": len(_ELEMENT_TYPES)}


_ENDSCREEN: YoutubeEndscreen | None = None


def get_youtube_endscreen() -> YoutubeEndscreen:
    """Get the module-level singleton endscreen helper."""
    global _ENDSCREEN
    if _ENDSCREEN is None:
        _ENDSCREEN = YoutubeEndscreen()
    return _ENDSCREEN
