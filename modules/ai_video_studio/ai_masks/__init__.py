"""Mask engine subsystem."""
from __future__ import annotations

from .mask_engine import MaskEngine, Mask
from .feather_engine import feather
from .edge_refinement import refine_mask
from .smart_masks import smart_mask

__all__ = ["MaskEngine", "Mask", "feather", "refine_mask", "smart_mask"]

engine = MaskEngine()
