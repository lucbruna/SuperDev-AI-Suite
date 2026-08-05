"""Restoration engine — chains restoration passes over a frame."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .denoise_video import denoise
from .deblur_video import deblur
from .scratch_removal import remove_scratches
from .dust_removal import remove_dust
from .super_resolution import upscale
from .color_restoration import restore_color


@dataclass
class RestorationConfig:
    denoise_strength: float = 0.3
    deblur_strength: float = 0.4
    remove_scratches: bool = False
    remove_dust: bool = False
    upscale_factor: float = 1.0
    color_restore: bool = False
    meta: dict[str, Any] = field(default_factory=dict)


class RestorationEngine:
    """Applies a configurable restoration pipeline."""

    def restore(self, frame: NDArray[np.floating], config: RestorationConfig | None = None) -> NDArray[np.floating]:
        cfg = config or RestorationConfig()
        out = frame.astype(np.float64)
        if cfg.denoise_strength > 0:
            out = denoise(out, strength=cfg.denoise_strength)
        if cfg.deblur_strength > 0:
            out = deblur(out, strength=cfg.deblur_strength)
        if cfg.remove_scratches:
            out = remove_scratches(out)
        if cfg.remove_dust:
            out = remove_dust(out)
        if cfg.color_restore:
            out = restore_color(out)
        if cfg.upscale_factor != 1.0:
            out = upscale(out, cfg.upscale_factor)
        return np.clip(out, 0.0, 1.0)

    def pipeline(self, name: str) -> RestorationConfig:
        """Named presets: 'old_movie', 'light', 'full'."""
        if name == "old_movie":
            return RestorationConfig(
                denoise_strength=0.35,
                deblur_strength=0.4,
                remove_scratches=True,
                remove_dust=True,
                color_restore=True,
            )
        if name == "light":
            return RestorationConfig(denoise_strength=0.15)
        if name == "full":
            return RestorationConfig(
                denoise_strength=0.5,
                deblur_strength=0.6,
                remove_scratches=True,
                remove_dust=True,
                color_restore=True,
                upscale_factor=2.0,
            )
        raise ValueError(f"unknown pipeline {name!r}")


restoration_engine = RestorationEngine()
