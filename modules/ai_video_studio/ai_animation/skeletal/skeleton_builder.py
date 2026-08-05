"""Skeleton builder — construct skeleton hierarchies for rigging."""
from __future__ import annotations

from typing import Any

_HUMAN_BONES = [
    ("root", None),
    ("hips", "root"),
    ("spine", "hips"),
    ("chest", "spine"),
    ("neck", "chest"),
    ("head", "neck"),
    ("shoulder_l", "chest"),
    ("arm_l", "shoulder_l"),
    ("forearm_l", "arm_l"),
    ("hand_l", "forearm_l"),
    ("shoulder_r", "chest"),
    ("arm_r", "shoulder_r"),
    ("forearm_r", "arm_r"),
    ("hand_r", "forearm_r"),
    ("thigh_l", "hips"),
    ("shin_l", "thigh_l"),
    ("foot_l", "shin_l"),
    ("thigh_r", "hips"),
    ("shin_r", "thigh_r"),
    ("foot_r", "shin_r"),
]


class SkeletonBuilder:
    """Builds a hierarchical skeleton from a bone list."""

    def build(self, *, bones: list[tuple[str, str | None]] | None = None) -> dict[str, Any]:
        bone_list = bones or _HUMAN_BONES
        nodes = {}
        for name, parent in bone_list:
            nodes[name] = {"name": name, "parent": parent, "children": []}
        for name, parent in bone_list:
            if parent is not None and parent in nodes:
                nodes[parent]["children"].append(name)
        return {"bones": nodes, "bone_names": [name for name, _ in bone_list]}

    def default_human(self) -> dict[str, Any]:
        return self.build()
