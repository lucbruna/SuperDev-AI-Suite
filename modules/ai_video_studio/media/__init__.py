"""Media output toolkit — real media generation for the AI Video Studio.

This package turns the logical engines (Volume 3) into producers of real
files. It provides:

* ``output_paths`` — canonical output directory (``modules/downloads/``).
* ``canvas`` — PIL/numpy based procedural canvas: gradients, noise,
  particles, shapes, text, camera transforms and style grading.
* ``video`` — assemble real MP4/WebM files from rendered frames using FFmpeg.
* ``llm`` — scene planning through a local Ollama model with a
  deterministic fallback planner, so generation always works offline.

Every module keeps working when a capability is missing: no Ollama → the
deterministic planner is used; no FFmpeg → frames are saved as an animated
GIF via Pillow.
"""
from modules.ai_video_studio.media.canvas import SceneCanvas
from modules.ai_video_studio.media.output_paths import get_downloads_dir, get_subsystem_dir
from modules.ai_video_studio.media.render import (
    render_multi_scene_video,
    render_scene_video,
    render_sim_frames,
    render_still,
)
from modules.ai_video_studio.media.video import frames_to_video
from modules.ai_video_studio.media.llm import ScenePlanner, get_scene_planner
from modules.ai_video_studio.media import audio, dsp, scene_narration, style_scenes

__all__ = [
    "SceneCanvas",
    "get_downloads_dir",
    "get_subsystem_dir",
    "render_multi_scene_video",
    "render_scene_video",
    "render_sim_frames",
    "render_still",
    "frames_to_video",
    "ScenePlanner",
    "get_scene_planner",
    "audio",
    "dsp",
    "scene_narration",
    "style_scenes",
]
