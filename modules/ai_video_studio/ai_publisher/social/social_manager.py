"""Social Manager — cross-platform social publishing orchestration (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_SUPPORTED = ["youtube", "tiktok", "instagram", "facebook", "linkedin", "x"]


class SocialManager:
    """Coordinate posts across multiple social platforms."""

    def __init__(self) -> None:
        self._cross_posts: list[dict] = []

    def supported_platforms(self) -> list[str]:
        return list(_SUPPORTED)

    def cross_post(self, *, content: dict, platforms: list[str]) -> dict:
        """Prepare content for several platforms at once."""
        unknown = [p for p in platforms if p not in _SUPPORTED]
        if unknown:
            return {"success": False, "error": f"Unsupported platforms: {unknown}"}
        post = {
            "platforms": list(platforms),
            "content": content,
            "adaptations": {p: self._adapt(content, p) for p in platforms},
        }
        self._cross_posts.append(post)
        return {"success": True, "post": post}

    @staticmethod
    def _adapt(content: dict, platform: str) -> dict:
        """Adapt generic content for a platform's constraints."""
        text = content.get("text", "")
        adapted = dict(content)
        if platform == "x":
            adapted["text"] = text[:280]
            adapted["max_chars"] = 280
        elif platform == "linkedin":
            adapted["max_chars"] = 3000
        elif platform == "instagram":
            adapted["max_chars"] = 2200
        elif platform == "tiktok":
            adapted["max_caption_chars"] = 2200
        else:
            adapted["max_chars"] = None
        return adapted

    def stats(self) -> dict[str, int]:
        return {"cross_posts": len(self._cross_posts)}


_MANAGER: SocialManager | None = None


def get_social_manager() -> SocialManager:
    """Get the module-level singleton social manager."""
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = SocialManager()
    return _MANAGER
