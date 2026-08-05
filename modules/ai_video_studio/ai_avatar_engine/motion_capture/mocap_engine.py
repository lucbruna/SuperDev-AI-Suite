"""Mocap engine — full motion-capture pipeline for the avatar engine.

Pipeline: keypoints → skeleton mapping → pose estimation → cleaning →
smoothing → (optional retarget) → classification → export.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_avatar_engine.motion_capture.animation_export import (
    get_animation_export,
)
from modules.ai_video_studio.ai_avatar_engine.motion_capture.motion_cleaner import (
    get_motion_cleaner,
)
from modules.ai_video_studio.ai_avatar_engine.motion_capture.motion_smoothing import (
    get_motion_smoothing,
)
from modules.ai_video_studio.ai_avatar_engine.motion_capture.movement_classifier import (
    get_movement_classifier,
)
from modules.ai_video_studio.ai_avatar_engine.motion_capture.pose_estimation import (
    get_pose_estimation,
)
from modules.ai_video_studio.ai_avatar_engine.motion_capture.skeleton_mapper import (
    get_skeleton_mapper,
)


class MocapEngine:
    """Processes keypoint streams into clean, exportable animation motion."""

    def process(
        self,
        keyframe_sources: list[dict[str, list[float] | tuple[float, float]]],
        *,
        fps: int = 24,
        smooth: float = 0.5,
        source_height: float = 1.8,
        target_height: float = 1.7,
        retarget: bool = False,
        export_path: str | Path | None = None,
    ) -> dict[str, Any]:
        mapper = get_skeleton_mapper()
        mapped = [mapper.map(k) for k in keyframe_sources]
        cleaned = get_motion_cleaner().clean(mapped)
        smoothed = get_motion_smoothing().smooth(cleaned, strength=smooth)
        if retarget:
            from modules.ai_video_studio.ai_avatar_engine.motion_capture.motion_retarget import (
                get_motion_retarget,
            )

            smoothed = get_motion_retarget().retarget(
                smoothed, source_height=source_height, target_height=target_height)

        label = get_movement_classifier().label(smoothed)
        pose = get_pose_estimation().estimate(smoothed[-1] if smoothed else {})

        result: dict[str, Any] = {
            "fps": fps,
            "frames": len(smoothed),
            "motion": smoothed,
            "label": label,
            "pose": pose,
        }
        if export_path:
            result["output_path"] = str(get_animation_export().export(
                smoothed, export_path, fps=fps, name=label))
        return result


_mocap_engine: MocapEngine | None = None


def get_mocap_engine() -> MocapEngine:
    """Return the shared mocap engine singleton."""
    global _mocap_engine
    if _mocap_engine is None:
        _mocap_engine = MocapEngine()
    return _mocap_engine
