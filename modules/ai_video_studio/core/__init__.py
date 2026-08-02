"""AI Video Studio Core - Foundation layer.

Provides configuration, constants, exceptions, and path management
for the entire video production platform.
"""
from modules.ai_video_studio.core.settings import VideoStudioSettings
from modules.ai_video_studio.core.constants import (
    Resolution, VideoCodec, AudioCodec, ContainerFormat,
    PixelFormat, ColorSpace, AspectRatio, FrameRate,
    SceneType, TransitionType, AssetType, ExportStatus,
    RenderPriority, QualityLevel
)
from modules.ai_video_studio.core.exceptions import (
    VideoStudioError, ValidationError, RenderingError,
    PipelineError, AssetError, ExportError, APIError
)

__all__ = [
    "VideoStudioSettings",
    "Resolution", "VideoCodec", "AudioCodec", "ContainerFormat",
    "PixelFormat", "ColorSpace", "AspectRatio", "FrameRate",
    "SceneType", "TransitionType", "AssetType", "ExportStatus",
    "RenderPriority", "QualityLevel",
    "VideoStudioError", "ValidationError", "RenderingError",
    "PipelineError", "AssetError", "ExportError", "APIError"
]