"""Export presets — named presets combining a profile, resolution and FPS.

Presets layer on top of :mod:`export_profiles` so callers can request a
high-level target (e.g. ``youtube_1080p``) without picking codecs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from modules.ai_video_studio.ai_export.export_profiles import ExportProfile, get_profile


@dataclass(frozen=True)
class ExportPreset:
    """A high-level named export target."""

    name: str
    profile: str
    resolution: tuple[int, int]  # (W, H)
    fps: int
    quality: str = "medium"
    extra_args: tuple[str, ...] = ()
    meta: dict[str, Any] = field(default_factory=dict)

    def resolve(self) -> tuple[ExportProfile, dict[str, Any]]:
        """Resolve to a concrete profile plus overrides for the renderer."""
        profile = get_profile(self.profile)
        return profile, {
            "resolution": self.resolution,
            "fps": self.fps,
            "quality": self.quality,
            "extra_args": self.extra_args,
        }


def _r(w: int, h: int) -> tuple[int, int]:
    return (w, h)


PRESETS: dict[str, ExportPreset] = {
    # Quality ladder
    "ultra_4k": ExportPreset("ultra_4k", "mp4_h265", _r(3840, 2160), 60, "high"),
    "full_hd": ExportPreset("full_hd", "mp4_h264", _r(1920, 1080), 30, "high"),
    "hd_720": ExportPreset("hd_720", "mp4_h264", _r(1280, 720), 30, "medium"),
    "sd_480": ExportPreset("sd_480", "mp4_h264", _r(854, 480), 30, "medium"),
    "master_prores": ExportPreset("master_prores", "mov_prores", _r(1920, 1080), 30, "master"),
    "master_prores_4k": ExportPreset("master_prores_4k", "mov_prores", _r(3840, 2160), 30, "master"),
    # Platform presets
    "youtube_1080p": ExportPreset("youtube_1080p", "mp4_h264", _r(1920, 1080), 30, "high"),
    "youtube_4k": ExportPreset("youtube_4k", "mp4_h265", _r(3840, 2160), 60, "high"),
    "instagram_reel": ExportPreset("instagram_reel", "mp4_h264", _r(1080, 1920), 30, "high"),
    "instagram_post": ExportPreset("instagram_post", "mp4_h264", _r(1080, 1080), 30, "high"),
    "tiktok": ExportPreset("tiktok", "mp4_h264", _r(1080, 1920), 30, "high"),
    "linkedin": ExportPreset("linkedin", "mp4_h264", _r(1920, 1080), 30, "medium"),
    "x_twitter": ExportPreset("x_twitter", "mp4_h264", _r(1920, 1080), 30, "medium"),
    "facebook": ExportPreset("facebook", "mp4_h264", _r(1920, 1080), 30, "medium"),
    "whatsapp": ExportPreset("whatsapp", "mp4_h264", _r(1280, 720), 30, "medium"),
    "web_webm": ExportPreset("web_webm", "webm_vp9", _r(1920, 1080), 30, "medium"),
    "gif_preview": ExportPreset("gif_preview", "gif", _r(640, 360), 15, "low"),
}

# Aliases that map to the canonical preset above
_PRESET_ALIASES = {
    "4k": "ultra_4k",
    "1080p": "full_hd",
    "720p": "hd_720",
    "480p": "sd_480",
    "youtube": "youtube_1080p",
    "instagram": "instagram_reel",
    "twitter": "x_twitter",
    "webm": "web_webm",
    "gif": "gif_preview",
}


def get_preset(name: str) -> ExportPreset:
    """Look up a preset by name (accepts aliases)."""
    key = _PRESET_ALIASES.get(name, name)
    if key not in PRESETS:
        raise KeyError(f"unknown export preset {name!r}; available: {sorted(PRESETS)}")
    return PRESETS[key]
