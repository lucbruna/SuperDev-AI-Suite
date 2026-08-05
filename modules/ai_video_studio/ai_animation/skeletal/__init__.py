"""Skeletal animation — skeleton, bones, rigging and IK."""
from modules.ai_video_studio.ai_animation.skeletal.skeleton_builder import SkeletonBuilder
from modules.ai_video_studio.ai_animation.skeletal.bone_mapper import BoneMapper
from modules.ai_video_studio.ai_animation.skeletal.rig_controller import RigController
from modules.ai_video_studio.ai_animation.skeletal.inverse_kinematics import InverseKinematics
from modules.ai_video_studio.ai_animation.skeletal.pose_optimizer import PoseOptimizer

__all__ = [
    "SkeletonBuilder",
    "BoneMapper",
    "RigController",
    "InverseKinematics",
    "PoseOptimizer",
]
