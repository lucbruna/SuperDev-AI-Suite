"""AI Color Grading — professional color correction (Volume 5).

Real per-frame grading pipeline (white balance, exposure, lift/gamma/gain,
temp/tint, saturation, contrast, LUT, curves), automatic and cinematic
grading, HDR tone mapping, LUTs, skin-tone protection and analysis scopes
(waveform, vectorscope, histogram).
"""
from modules.ai_video_studio.ai_color_grading.grading_engine import GradePipeline
from modules.ai_video_studio.ai_color_grading.automatic_grading import AutomaticGrading
from modules.ai_video_studio.ai_color_grading.cinematic_grading import CinematicGrading
from modules.ai_video_studio.ai_color_grading.hdr_engine import HdrEngine
from modules.ai_video_studio.ai_color_grading.lut_manager import LutManager
from modules.ai_video_studio.ai_color_grading.lut_library import LutLibrary
from modules.ai_video_studio.ai_color_grading.white_balance import WhiteBalance
from modules.ai_video_studio.ai_color_grading.color_match import ColorMatch
from modules.ai_video_studio.ai_color_grading.skin_tone_optimizer import SkinToneOptimizer
from modules.ai_video_studio.ai_color_grading.exposure_controller import ExposureController
from modules.ai_video_studio.ai_color_grading.contrast_controller import ContrastController
from modules.ai_video_studio.ai_color_grading.saturation_controller import SaturationController
from modules.ai_video_studio.ai_color_grading.highlight_recovery import HighlightRecovery
from modules.ai_video_studio.ai_color_grading.shadow_recovery import ShadowRecovery
from modules.ai_video_studio.ai_color_grading.curves_editor import CurvesEditor
from modules.ai_video_studio.ai_color_grading.color_wheels import ColorWheels
from modules.ai_video_studio.ai_color_grading.scopes_waveform import ScopesWaveform
from modules.ai_video_studio.ai_color_grading.scopes_vectorscope import ScopesVectorscope
from modules.ai_video_studio.ai_color_grading.histogram import Histogram

__all__ = [
    "GradePipeline",
    "AutomaticGrading",
    "CinematicGrading",
    "HdrEngine",
    "LutManager",
    "LutLibrary",
    "WhiteBalance",
    "ColorMatch",
    "SkinToneOptimizer",
    "ExposureController",
    "ContrastController",
    "SaturationController",
    "HighlightRecovery",
    "ShadowRecovery",
    "CurvesEditor",
    "ColorWheels",
    "ScopesWaveform",
    "ScopesVectorscope",
    "Histogram",
]
