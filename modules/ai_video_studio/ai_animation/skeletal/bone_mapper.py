"""Bone mapper — map skeleton names across conventions."""
from __future__ import annotations

from typing import Any

_ALIASES = {
    "leg_left": "thigh_l",
    "leg_right": "thigh_r",
    "arm_left": "arm_l",
    "arm_right": "arm_r",
    "left_hand": "hand_l",
    "right_hand": "hand_r",
    "pelvis": "hips",
    "chest": "chest",
    "spine_01": "spine",
    "head": "head",
}


class BoneMapper:
    """Normalises bone names between different rig conventions."""

    def map(self, bone_name: str) -> str:
        return _ALIASES.get(bone_name, bone_name)

    def map_pose(self, pose: dict[str, Any]) -> dict[str, Any]:
        return {self.map(name): value for name, value in pose.items()}

    def register_alias(self, alias: str, canonical: str) -> None:
        _ALIASES[alias] = canonical
