"""Runtime feature flags for enabling/disabling capabilities.

Flags are read from environment variables VIDEO_STUDIO_FLAG_<name>=1|0.
Defaults are defined here and can be overridden at startup.
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field


@dataclass
class FeatureFlags:
    gpu_rendering: bool = False
    ai_generation: bool = True
    voice_clone: bool = False
    live_streaming: bool = False
    collaborative_editing: bool = False
    advanced_analytics: bool = True
    batch_processing: bool = True
    auto_subtitles: bool = True
    watermark_protection: bool = False
    drm_protection: bool = False

    def load_from_env(self) -> None:
        prefix = "VIDEO_STUDIO_FLAG_"
        for fld in self.__dataclass_fields__:
            env_key = prefix + fld.upper()
            val = os.environ.get(env_key, "")
            if val in ("1", "true", "True", "yes"):
                setattr(self, fld, True)
            elif val in ("0", "false", "False", "no"):
                setattr(self, fld, False)

    def as_dict(self) -> dict[str, bool]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


_flags: FeatureFlags | None = None


def get_flags() -> FeatureFlags:
    global _flags
    if _flags is None:
        _flags = FeatureFlags()
        _flags.load_from_env()
    return _flags