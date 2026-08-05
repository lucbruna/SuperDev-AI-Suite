"""Avatar Engine — core orchestrator of the AI Avatar & Digital Human Engine.

The engine is the public entry point of the ``ai_avatar_engine`` package
(blueprint Volume 6). It wires the subsystems together:

* profiles → identity (who the presenter is),
* digital humans → body/face/clothing/hairstyle generation,
* facial animation + emotions + gestures → per-frame performance,
* motion capture → retargeted motion from sources,
* library → domain-specific virtual actors,
* training → learning/personalization,
* scheduler/optimizer/statistics/cache/logger → cross-cutting concerns.

Subsystem imports are lazy so the core engine works even when an optional
subsystem is not installed.
"""
from __future__ import annotations

import time
from typing import Any

from modules.ai_video_studio.ai_avatar_engine.avatar_cache import AvatarCache, get_avatar_cache
from modules.ai_video_studio.ai_avatar_engine.avatar_learning import AvatarLearning, get_avatar_learning
from modules.ai_video_studio.ai_avatar_engine.avatar_logger import AvatarLogger, get_avatar_logger
from modules.ai_video_studio.ai_avatar_engine.avatar_manager import AvatarManager, get_avatar_manager
from modules.ai_video_studio.ai_avatar_engine.avatar_metadata import get_avatar_metadata
from modules.ai_video_studio.ai_avatar_engine.avatar_optimizer import AvatarOptimizer, get_avatar_optimizer
from modules.ai_video_studio.ai_avatar_engine.avatar_permissions import get_avatar_permissions
from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile
from modules.ai_video_studio.ai_avatar_engine.avatar_registry import AvatarRegistry, get_avatar_registry
from modules.ai_video_studio.ai_avatar_engine.avatar_scheduler import AvatarScheduler, get_avatar_scheduler
from modules.ai_video_studio.ai_avatar_engine.avatar_statistics import AvatarStatistics, get_avatar_statistics
from modules.ai_video_studio.core.exceptions import ValidationError


class AvatarEngine:
    """Public orchestrator for the avatar engine subsystem."""

    def __init__(
        self,
        *,
        registry: AvatarRegistry | None = None,
        manager: AvatarManager | None = None,
    ) -> None:
        self.registry = registry or get_avatar_registry()
        self.manager = manager or get_avatar_manager()
        self.scheduler: AvatarScheduler = get_avatar_scheduler()
        self.optimizer: AvatarOptimizer = get_avatar_optimizer()
        self.learning: AvatarLearning = get_avatar_learning()
        self.statistics: AvatarStatistics = get_avatar_statistics()
        self.cache: AvatarCache = get_avatar_cache()
        self.logger: AvatarLogger = get_avatar_logger()
        self._jobs: dict[str, dict[str, Any]] = {}

    # ── profile management ────────────────────────────────────────
    def register_profile(self, profile: AvatarProfile) -> bool:
        """Register a profile with the shared registry (idempotent)."""
        return self.manager.register(profile)

    def get_profile(self, profile_id: str) -> AvatarProfile:
        return self.manager.get(profile_id)

    def list_profiles(self, **filters: Any) -> list[AvatarProfile]:
        return self.manager.list(**filters)

    def profiles_dicts(self, **filters: Any) -> list[dict[str, Any]]:
        return [p.to_dict() for p in self.list_profiles(**filters)]

    # ── generation pipeline ───────────────────────────────────────
    def generate_avatar(
        self,
        profile: AvatarProfile,
        *,
        quality: str = "high",
        fps: int = 24,
        resolution: str = "1280x720",
        seed: int | None = None,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate a digital-human presenter for a profile.

        Delegates to the ``digital_humans`` subsystem when available, else
        returns a deterministic descriptor. Records statistics and caching.
        """
        started = time.time()
        if quality not in ("draft", "high", "final"):
            raise ValidationError(f"Unknown quality '{quality}'", field="quality")
        rid = job_id or f"avatar_{len(self._jobs) + 1}"

        settings = self.optimizer.optimize(quality=quality, fps=fps, resolution=resolution)
        cache_key = f"gen:{profile.id}:{quality}:{fps}:{resolution}:{seed or 0}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            self.logger.info("cache_hit", job=rid, profile=profile.id, cache_key=cache_key)
            self._jobs[rid] = cached
            return cached

        self.logger.info("generate_avatar", job=rid, profile=profile.id, quality=quality)
        result: dict[str, Any] = {
            "id": rid,
            "profile": profile.to_dict(),
            "settings": settings,
            "status": "ok",
            "seed": seed,
        }
        try:
            from modules.ai_video_studio.ai_avatar_engine.digital_humans.digital_human_engine import (
                get_digital_human_engine,
            )

            generated = get_digital_human_engine().generate(profile, settings=settings, seed=seed)
            result.update(generated)
        except Exception as e:  # noqa: BLE001 — subsystem optional
            self.logger.warn("digital_humans_unavailable", job=rid, error=str(e))
            result["components"] = self._descriptor(profile, settings)

        result["elapsed_seconds"] = round(time.time() - started, 3)
        result = get_avatar_metadata().enrich(result, profile)
        self.cache.put(cache_key, result)
        self.statistics.record(style=profile.style, dimension=profile.dimension,
                               duration_ms=result["elapsed_seconds"] * 1000)
        self._jobs[rid] = result
        return result

    # ── jobs / introspection ──────────────────────────────────────
    def get_job(self, job_id: str) -> dict[str, Any] | None:
        return dict(self._jobs[job_id]) if job_id in self._jobs else None

    def list_jobs(self) -> list[str]:
        return list(self._jobs)

    def stats(self) -> dict[str, Any]:
        return {
            "profiles": self.registry.profile_count(),
            "jobs": len(self._jobs),
            "summary": self.statistics.summary(),
            "cache": len(self.cache),
        }

    def check_permission(self, role: str, action: str) -> bool:
        return get_avatar_permissions().check(role, action)

    # ── helpers ───────────────────────────────────────────────────
    @staticmethod
    def _descriptor(profile: AvatarProfile, settings: dict[str, Any]) -> dict[str, Any]:
        """Deterministic structural descriptor (fallback when no renderer)."""
        return {
            "head": {"shape": "oval", "skin": profile.skin_tone},
            "hair": {"style": profile.hair_style, "color": profile.hair_color},
            "eyes": {"color": profile.eye_color},
            "body": {"build": profile.build, "height_cm": profile.height_cm},
            "clothing": {"outfit": profile.default_outfit},
            "quality": settings.get("quality", "high"),
        }


_avatar_engine: AvatarEngine | None = None


def get_avatar_engine() -> AvatarEngine:
    """Return the shared avatar engine singleton."""
    global _avatar_engine
    if _avatar_engine is None:
        _avatar_engine = AvatarEngine()
    return _avatar_engine
