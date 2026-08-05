"""Pose estimation — derive joint angles from mapped keypoints."""
from __future__ import annotations

import math
from typing import Any


class PoseEstimation:
    """Computes normalized joint angles from a mapped skeleton."""

    def estimate(self, skeleton: dict[str, tuple[float, float]]) -> dict[str, Any]:
        def _angle(a: str, b: str, c: str) -> float | None:
            pa, pb, pc = skeleton.get(a), skeleton.get(b), skeleton.get(c)
            if not (pa and pb and pc):
                return None
            v1 = (pa[0] - pb[0], pa[1] - pb[1])
            v2 = (pc[0] - pb[0], pc[1] - pb[1])
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            mag = math.hypot(*v1) * math.hypot(*v2) + 1e-9
            return math.degrees(math.acos(max(-1.0, min(1.0, dot / mag))))

        return {
            "elbow_left_deg": _angle("shoulder_l", "elbow_l", "wrist_l"),
            "elbow_right_deg": _angle("shoulder_r", "elbow_r", "wrist_r"),
            "knee_left_deg": _angle("hip_l", "knee_l", "ankle_l"),
            "knee_right_deg": _angle("hip_r", "knee_r", "ankle_r"),
            "arm_lift_left": _arm_lift(skeleton.get("shoulder_l"), skeleton.get("wrist_l")),
            "arm_lift_right": _arm_lift(skeleton.get("shoulder_r"), skeleton.get("wrist_r")),
        }


def _arm_lift(shoulder: tuple[float, float] | None, wrist: tuple[float, float] | None) -> float | None:
    if not (shoulder and wrist):
        return None
    return round(max(-1.0, min(1.0, (shoulder[1] - wrist[1]) * 3.0)), 3)


_pose_estimation: PoseEstimation | None = None


def get_pose_estimation() -> PoseEstimation:
    global _pose_estimation
    if _pose_estimation is None:
        _pose_estimation = PoseEstimation()
    return _pose_estimation
