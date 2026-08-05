"""Skeleton mapper — maps arbitrary joint names to the avatar skeleton."""
from __future__ import annotations


# Canonical avatar skeleton joints.
AVATAR_JOINTS = (
    "head", "neck", "shoulder_l", "shoulder_r", "elbow_l", "elbow_r",
    "wrist_l", "wrist_r", "hip_l", "hip_r", "knee_l", "knee_r",
    "ankle_l", "ankle_r", "chest", "pelvis",
)

# Common external aliases → avatar joints.
_ALIASES: dict[str, str] = {
    "nose": "head", "head_top": "head", "neck": "neck",
    "left_shoulder": "shoulder_l", "right_shoulder": "shoulder_r",
    "left_elbow": "elbow_l", "right_elbow": "elbow_r",
    "left_wrist": "wrist_l", "right_wrist": "wrist_r",
    "left_hip": "hip_l", "right_hip": "hip_r",
    "left_knee": "knee_l", "right_knee": "knee_r",
    "left_ankle": "ankle_l", "right_ankle": "ankle_r",
    "chest": "chest", "pelvis": "pelvis",
}


class SkeletonMapper:
    """Maps external keypoints onto the avatar skeleton (alias table)."""

    def map(self, keypoints: dict[str, list[float] | tuple[float, float]]) -> dict[str, tuple[float, float]]:
        mapped: dict[str, tuple[float, float]] = {}
        for key, value in keypoints.items():
            target = _ALIASES.get(key)
            if target is None:
                continue
            if len(value) < 2:
                continue
            mapped[target] = (float(value[0]), float(value[1]))
        return mapped

    def joints(self) -> list[str]:
        return list(AVATAR_JOINTS)


_skeleton_mapper: SkeletonMapper | None = None


def get_skeleton_mapper() -> SkeletonMapper:
    global _skeleton_mapper
    if _skeleton_mapper is None:
        _skeleton_mapper = SkeletonMapper()
    return _skeleton_mapper
