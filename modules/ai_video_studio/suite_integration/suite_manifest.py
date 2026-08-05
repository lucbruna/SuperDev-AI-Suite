"""Suite manifest — the AI Video Studio's platform contract (Volume 10).

Declares, in one place, which SuperDev platform services the studio
*consumes* (reuses instead of re-implementing) and which studio
capabilities it *provides* back to the platform. This is the single source
of truth surfaced by ``GET /suite-integration/manifest`` and consumed by
the :class:`SuiteBridge` for registration and capability reporting.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MODULE_NAME = "ai_video_studio"
SUITE_VERSION = "1.0.0"


@dataclass(frozen=True)
class SuiteManifest:
    """Declarative contract between the AI Video Studio and the suite."""

    module: str = MODULE_NAME
    version: str = SUITE_VERSION

    #: Platform services the studio reuses (never duplicated).
    consumes: tuple[str, ...] = (
        "auth",                # backend.auth.jwt — JWT verification
        "security.ssrf",       # SuperDev.security.ssrf — SSRF guards
        "observability",       # SuperDev.monitoring — metrics/health
        "workflow",            # SuperDev.workflow — pipeline registration
        "integration",         # SuperDev.integration — integration engine
        "plugins",             # SuperDev.plugin_platform — plugin platform
    )

    #: Studio capabilities exposed back to the platform.
    provides: tuple[str, ...] = (
        "video_studio",        # text/image/video-to-video generation
        "voice_studio",        # TTS narration (edge-tts → formant)
        "avatar_engine",       # digital humans & virtual actors
        "speaking_avatar",     # narrated lip-synced presenter videos
        "lip_sync",            # viseme timelines from audio
        "editing",             # timeline/effects/grading
        "export",              # multi-format export & render queue
    )

    #: Studio services registered in the studio's own integration manager.
    services: tuple[str, ...] = (
        "ai_studio", "voice_studio", "avatar_engine", "subtitle_studio",
        "export_service", "render_engine", "suite_bridge",
    )

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "version": self.version,
            "consumes": list(self.consumes),
            "provides": list(self.provides),
            "services": list(self.services),
            "metadata": dict(self.metadata),
        }


SUITE_MANIFEST = SuiteManifest()
