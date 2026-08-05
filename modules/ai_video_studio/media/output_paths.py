"""Output paths — where generated media is written.

The user requested all generated files land in ``modules/downloads/``.
Sub-systems get their own subfolder::

    modules/downloads/
        images/        AI Image Generator
        videos/        AI Video Generator (text/image/video to video)
        animations/    AI Animation Engine
        camera/        AI Camera Engine test renders
        physics/       AI Physics Engine simulations
        assets/        Asset Library generated placeholders
"""
from __future__ import annotations

from pathlib import Path

# output_paths.py lives at <project>/modules/ai_video_studio/media/
_MEDIA_DIR = Path(__file__).resolve().parent          # .../media
_STUDIO_DIR = _MEDIA_DIR.parent                        # .../ai_video_studio
_PROJECT_ROOT = _STUDIO_DIR.parent.parent              # <project>/ (SuperDev/)

# The user asked for downloads to live under <project>/modules/downloads
DOWNLOADS_DIR = _PROJECT_ROOT / "modules" / "downloads"

_SUBDIRS = {
    "images": "images",
    "videos": "videos",
    "animations": "animations",
    "camera": "camera",
    "physics": "physics",
    "assets": "assets",
    # Volume 4 — AI Voice/Audio Studio
    "voice": "voice",
    "clones": "voice_clones",
    "dubbing": "dubbing",
    "lip_sync": "lip_sync",
    "music": "music",
    "effects": "effects",
    "mix": "mix",
    "subtitles": "subtitles",
    # Volume 6 — AI Avatar & Digital Human Engine
    "avatars": "avatars",
    # Volume 5 — Distribution & growth
    "branding": "branding",
    "seo": "seo",
    "marketing": "marketing",
    "thumbnails": "thumbnails",
}


def get_downloads_dir() -> Path:
    """Return the root downloads directory, creating it if needed."""
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    return DOWNLOADS_DIR


def get_subsystem_dir(kind: str) -> Path:
    """Return the subdirectory for a subsystem (e.g. ``"images"``)."""
    sub = _SUBDIRS.get(kind, kind)
    path = DOWNLOADS_DIR / sub
    path.mkdir(parents=True, exist_ok=True)
    return path


def media_path(kind: str, filename: str) -> Path:
    """Return a unique path inside a subsystem directory."""
    return get_subsystem_dir(kind) / filename


def unique_filename(directory: Path, prefix: str, extension: str) -> Path:
    """Return a collision-free ``prefix_<n>.<extension>`` path."""
    directory.mkdir(parents=True, exist_ok=True)
    counter = 1
    while True:
        candidate = directory / f"{prefix}_{counter:04d}.{extension}"
        if not candidate.exists():
            return candidate
        counter += 1
