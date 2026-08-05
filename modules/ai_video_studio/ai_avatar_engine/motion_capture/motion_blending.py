"""Motion blending — cross-fade between two motion streams."""
from __future__ import annotations



class MotionBlending:
    """Blends two frame streams with a normalized weight per frame."""

    def blend(self, a: list[dict[str, tuple[float, float]]],
              b: list[dict[str, tuple[float, float]]],
              weights: list[float]) -> list[dict[str, tuple[float, float]]]:
        count = max(len(a), len(b))
        out: list[dict[str, tuple[float, float]]] = []
        for i in range(count):
            fa = a[i] if i < len(a) else {}
            fb = b[i] if i < len(b) else {}
            w = weights[i] if i < len(weights) else 0.5
            w = max(0.0, min(1.0, w))
            joints = set(fa) | set(fb)
            blended = {}
            for joint in joints:
                if joint in fa and joint in fb:
                    x = fa[joint][0] * (1 - w) + fb[joint][0] * w
                    y = fa[joint][1] * (1 - w) + fb[joint][1] * w
                    blended[joint] = (round(x, 4), round(y, 4))
                else:
                    blended[joint] = fa.get(joint) or fb.get(joint)
            out.append(blended)
        return out


_motion_blending: MotionBlending | None = None


def get_motion_blending() -> MotionBlending:
    global _motion_blending
    if _motion_blending is None:
        _motion_blending = MotionBlending()
    return _motion_blending
