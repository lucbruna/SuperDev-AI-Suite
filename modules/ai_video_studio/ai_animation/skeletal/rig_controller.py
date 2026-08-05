"""Rig controller — drive a skeleton through posed keyframes."""
from __future__ import annotations

from typing import Any


class RigController:
    """Applies rotation/translation values to skeleton bones."""

    def __init__(self, skeleton: dict[str, Any] | None = None) -> None:
        self.skeleton = skeleton or {}
        self._pose: dict[str, dict[str, float]] = {}

    def set_pose(self, bone: str, *, rx: float = 0.0, ry: float = 0.0, rz: float = 0.0) -> None:
        self._pose[bone] = {"rx": rx, "ry": ry, "rz": rz}

    def apply_pose(self, bone: str) -> dict[str, float] | None:
        return dict(self._pose[bone]) if bone in self._pose else None

    def clear(self) -> None:
        self._pose.clear()

    def snapshot(self) -> dict[str, Any]:
        return {"pose": dict(self._pose), "bone_count": len(self.skeleton.get("bone_names", []))}
