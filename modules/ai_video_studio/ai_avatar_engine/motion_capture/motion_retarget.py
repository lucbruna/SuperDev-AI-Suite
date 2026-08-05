"""Motion retarget — retarget motion between skeletons of different scales."""
from __future__ import annotations



class MotionRetarget:
    """Scales/translates joint positions onto a target body scale."""

    def retarget(self, frames: list[dict[str, tuple[float, float]]],
                 *, source_height: float = 1.8, target_height: float = 1.7) -> list[dict[str, tuple[float, float]]]:
        scale = target_height / max(source_height, 1e-9)
        retargeted: list[dict[str, tuple[float, float]]] = []
        for frame in frames:
            out = {joint: (round(x * scale, 4), round(y * scale, 4))
                   for joint, (x, y) in frame.items()}
            retargeted.append(out)
        return retargeted


_motion_retarget: MotionRetarget | None = None


def get_motion_retarget() -> MotionRetarget:
    global _motion_retarget
    if _motion_retarget is None:
        _motion_retarget = MotionRetarget()
    return _motion_retarget
