"""Publisher Engine — orchestrates multi-platform publishing (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_PLATFORM_MODULES = {
    "social": "modules.ai_video_studio.ai_publisher.social",
    "youtube": "modules.ai_video_studio.ai_publisher.youtube",
    "tiktok": "modules.ai_video_studio.ai_publisher.tiktok",
    "instagram": "modules.ai_video_studio.ai_publisher.instagram",
    "facebook": "modules.ai_video_studio.ai_publisher.facebook",
    "linkedin": "modules.ai_video_studio.ai_publisher.linkedin",
    "x": "modules.ai_video_studio.ai_publisher.x_platform",
    "seo": "modules.ai_video_studio.ai_publisher.seo",
    "analytics": "modules.ai_video_studio.ai_publisher.analytics",
}


class PublisherEngine:
    """Coordinate queue, scheduler, platform clients and reporting."""

    def __init__(self) -> None:
        self._started_at = 0.0
        self._publish_count = 0

    def _platform_ready(self, platform: str) -> bool:
        """Resolve a platform subpackage lazily (may not exist yet)."""
        module_path = _PLATFORM_MODULES.get(platform)
        if not module_path:
            return False
        try:
            __import__(module_path)
            return True
        except ImportError:
            return False

    def available_platforms(self) -> list[str]:
        """List platform names whose subpackages exist."""
        return [name for name in _PLATFORM_MODULES if self._platform_ready(name)]

    def publish(self, *, content: dict, platforms: list[str]) -> dict:
        """Enqueue content for one or more platforms via the queue singleton."""
        from modules.ai_video_studio.ai_publisher.publisher_queue import get_publisher_queue

        missing = [p for p in platforms if not self._platform_ready(p)]
        if missing:
            return {"success": False, "error": f"Unknown platforms: {missing}"}
        job = get_publisher_queue().enqueue(content=content, platforms=platforms)
        self._publish_count += 1
        return {"success": True, "job": job}

    def schedule(self, *, content: dict, platforms: list[str], schedule_at: float | None = None) -> dict:
        """Schedule content for future publication."""
        from modules.ai_video_studio.ai_publisher.publisher_queue import get_publisher_queue

        missing = [p for p in platforms if not self._platform_ready(p)]
        if missing:
            return {"success": False, "error": f"Unknown platforms: {missing}"}
        job = get_publisher_queue().enqueue(
            content=content, platforms=platforms, schedule_at=schedule_at
        )
        return {"success": True, "job": job}

    def get_status(self) -> dict:
        """Return current engine status with platform availability."""
        from modules.ai_video_studio.ai_publisher.publisher_queue import get_publisher_queue

        return {
            "started": bool(self._started_at),
            "publishes_queued": get_publisher_queue().pending_count(),
            "available_platforms": self.available_platforms(),
        }

    def stats(self) -> dict[str, int]:
        return {"publishes": self._publish_count}


_ENGINE: PublisherEngine | None = None


def get_publisher_engine() -> PublisherEngine:
    """Get the module-level singleton engine."""
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = PublisherEngine()
    return _ENGINE
