"""Video to Video — transform an existing video into a new one.

Style transfer, restoration, frame enhancement, upscaling, fps conversion,
noise removal, background editing, segmentation, scene detection and motion
analysis.
"""
from modules.ai_video_studio.ai_video_generator.video_to_video.video_converter import VideoConverter
from modules.ai_video_studio.ai_video_generator.video_to_video.style_transfer import StyleTransfer
from modules.ai_video_studio.ai_video_generator.video_to_video.video_restoration import VideoRestoration
from modules.ai_video_studio.ai_video_generator.video_to_video.frame_enhancer import FrameEnhancer
from modules.ai_video_studio.ai_video_generator.video_to_video.video_upscaler import VideoUpscaler
from modules.ai_video_studio.ai_video_generator.video_to_video.fps_converter import FPSConverter
from modules.ai_video_studio.ai_video_generator.video_to_video.noise_removal import NoiseRemoval
from modules.ai_video_studio.ai_video_generator.video_to_video.background_editor import BackgroundEditor
from modules.ai_video_studio.ai_video_generator.video_to_video.video_segmentation import VideoSegmentation
from modules.ai_video_studio.ai_video_generator.video_to_video.scene_detector import SceneDetector
from modules.ai_video_studio.ai_video_generator.video_to_video.motion_analyzer import MotionAnalyzer

__all__ = [
    "VideoConverter",
    "StyleTransfer",
    "VideoRestoration",
    "FrameEnhancer",
    "VideoUpscaler",
    "FPSConverter",
    "NoiseRemoval",
    "BackgroundEditor",
    "VideoSegmentation",
    "SceneDetector",
    "MotionAnalyzer",
]
