"""Publisher Manager — platform registry and publish job orchestration (Volume 7)."""
from __future__ import annotations

import logging
import time
import uuid

logger = logging.getLogger(__name__)

PLATFORM_NAMES = ["social", "youtube", "tiktok", "instagram", "facebook", "linkedin", "x"]


class PublisherManager:
    """Manage platform registry, content packages and publish jobs."""

    def __init__(self) -> None:
        self._platforms: dict[str, dict] = {
            name: {"name": name, "configured": False, "enabled": True} for name in PLATFORM_NAMES
        }
        self._jobs: dict[str, dict] = {}

    def register_platform(self, *, name: str, configured: bool = False, enabled: bool = True) -> dict:
        """Register or update a platform entry."""
        if not name:
            return {"success": False, "error": "Platform name required"}
        self._platforms[name] = {"name": name, "configured": bool(configured), "enabled": bool(enabled)}
        return {"success": True, "platform": self._platforms[name]}

    def list_platforms(self) -> list[dict]:
        return list(self._platforms.values())

    def create_job(self, *, content: dict, platforms: list[str]) -> dict:
        """Register a content package for publishing."""
        job_id = uuid.uuid4().hex[:12]
        job = {
            "job_id": job_id,
            "content": content,
            "platforms": list(platforms),
            "created_at": time.time(),
            "status": "created",
        }
        self._jobs[job_id] = job
        logger.info("Created publisher job %s", job_id)
        return job

    def get_job(self, job_id: str) -> dict | None:
        return self._jobs.get(job_id)

    def list_jobs(self) -> list[dict]:
        return sorted(self._jobs.values(), key=lambda j: j["created_at"], reverse=True)

    def stats(self) -> dict[str, int]:
        return {"platforms": len(self._platforms), "jobs": len(self._jobs)}


_MANAGER: PublisherManager | None = None


def get_publisher_manager() -> PublisherManager:
    """Get the module-level singleton manager."""
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = PublisherManager()
    return _MANAGER
