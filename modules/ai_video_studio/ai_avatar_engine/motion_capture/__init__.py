"""Motion Capture — pose estimation, retargeting and motion cleaning.

Takes keypoint sources (external trackers or synthetic), maps them onto the
avatar skeleton, cleans/smooths the signal and exports animation data.
"""
from modules.ai_video_studio.ai_avatar_engine.motion_capture.mocap_engine import (
    MocapEngine,
    get_mocap_engine,
)

__all__ = ["MocapEngine", "get_mocap_engine"]
