"""Version information for AI Video Studio.

Provides version constants, compatibility checking, and build metadata
used throughout the platform for health checks and diagnostics.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date


__version__ = "1.0.0"
__version_info__ = tuple(__version__.split("."))
BUILD_DATE = "2026-08-02"
PYTHON_REQUIRES = ">=3.11"
MIN_FFMPEG_VERSION = "4.4"


@dataclass(frozen=True)
class BuildInfo:
    """Immutable snapshot of the current build."""

    version: str = __version__
    build_date: str = BUILD_DATE
    python_requires: str = PYTHON_REQUIRES
    min_ffmpeg: str = MIN_FFMPEG_VERSION

    @property
    def major(self) -> int:
        return int(__version_info__[0])

    @property
    def minor(self) -> int:
        return int(__version_info__[1])

    @property
    def patch(self) -> int:
        return int(__version_info__[2])

    def is_compatible(self, other_version: str) -> bool:
        """Check if *other_version* is compatible (same major)."""
        other_parts = tuple(other_version.split("."))
        try:
            return int(other_parts[0]) == self.major
        except (ValueError, IndexError):
            return False

    def to_dict(self) -> dict[str, str]:
        return {
            "version": self.version,
            "build_date": self.build_date,
            "python_requires": self.python_requires,
            "min_ffmpeg": self.min_ffmpeg,
        }


# Module-level singleton
build_info = BuildInfo()
