"""AI Video Studio — AI Restoration (Volume 5).

Restores damaged, old, low-quality footage: denoise, deblur, scratch/dust
removal, super-resolution, frame reconstruction, FPS reconstruction and
vintage film restoration. All helpers operate on float frames in [0, 1].
"""
from __future__ import annotations

from modules.ai_video_studio.ai_restoration.denoise_video import denoise
from modules.ai_video_studio.ai_restoration.deblur_video import deblur
from modules.ai_video_studio.ai_restoration.scratch_removal import remove_scratches
from modules.ai_video_studio.ai_restoration.dust_removal import remove_dust
from modules.ai_video_studio.ai_restoration.super_resolution import upscale, fast_upscale
from modules.ai_video_studio.ai_restoration.frame_reconstruction import reconstruct_frame, fill_gaps
from modules.ai_video_studio.ai_restoration.color_restoration import restore_color
from modules.ai_video_studio.ai_restoration.restoration_engine import RestorationEngine, RestorationConfig, restoration_engine
from modules.ai_video_studio.ai_restoration.fps_reconstruction import fps_reconstruction, FPSReconstruction
from modules.ai_video_studio.ai_restoration.damaged_frame_repair import damaged_frame_repair, DamagedFrameRepair
from modules.ai_video_studio.ai_restoration.old_movie_restoration import old_movie_restoration, OldMovieRestoration

__all__ = [
    "denoise",
    "deblur",
    "remove_scratches",
    "remove_dust",
    "upscale",
    "fast_upscale",
    "reconstruct_frame",
    "fill_gaps",
    "restore_color",
    "RestorationEngine",
    "RestorationConfig",
    "restoration_engine",
    "fps_reconstruction",
    "FPSReconstruction",
    "damaged_frame_repair",
    "DamagedFrameRepair",
    "old_movie_restoration",
    "OldMovieRestoration",
]
