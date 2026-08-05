"""AI Camera Engine — virtual cinematography (blueprint Volume 3).

Virtual cameras, parametric paths, presets, follow behaviour, cinematic,
drone, handheld, orbit and crane moves, zoom, focus, dolly, gimbal and
stabilisation.
"""
from modules.ai_video_studio.ai_camera.camera_engine import CameraEngine, get_camera_engine
from modules.ai_video_studio.ai_camera.virtual_camera import VirtualCamera
from modules.ai_video_studio.ai_camera.camera_paths import CameraPaths
from modules.ai_video_studio.ai_camera.camera_presets import CameraPresets
from modules.ai_video_studio.ai_camera.camera_follow import CameraFollow
from modules.ai_video_studio.ai_camera.cinematic_camera import CinematicCamera
from modules.ai_video_studio.ai_camera.drone_camera import DroneCamera
from modules.ai_video_studio.ai_camera.handheld_camera import HandheldCamera
from modules.ai_video_studio.ai_camera.orbit_camera import OrbitCamera
from modules.ai_video_studio.ai_camera.zoom_controller import ZoomController
from modules.ai_video_studio.ai_camera.focus_controller import FocusController
from modules.ai_video_studio.ai_camera.dolly_controller import DollyController
from modules.ai_video_studio.ai_camera.crane_controller import CraneController
from modules.ai_video_studio.ai_camera.gimbal_controller import GimbalController
from modules.ai_video_studio.ai_camera.stabilization import Stabilization

__all__ = [
    "CameraEngine",
    "get_camera_engine",
    "VirtualCamera",
    "CameraPaths",
    "CameraPresets",
    "CameraFollow",
    "CinematicCamera",
    "DroneCamera",
    "HandheldCamera",
    "OrbitCamera",
    "ZoomController",
    "FocusController",
    "DollyController",
    "CraneController",
    "GimbalController",
    "Stabilization",
]
