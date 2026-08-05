"""Facial Sync — merges all controllers into a single per-frame record."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_lip_sync.blink_sync import apply_blinks
from modules.ai_video_studio.ai_lip_sync.expression_controller import expression_curve


def build_facial_timeline(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return frames enriched with blinks and expression blendshapes."""
    frames = apply_blinks(frames)
    expressions = expression_curve(frames)
    expr_by_frame = {e["frame"]: e for e in expressions}
    out: list[dict[str, Any]] = []
    for f in frames:
        expr = expr_by_frame.get(f.get("frame"), {})
        out.append({
            **f,
            "blink": f.get("_blink", 1.0),
            "expression": {
                "smile": expr.get("smile", 0.0),
                "surprise": expr.get("surprise", 0.0),
                "neutral": expr.get("neutral", 1.0),
            },
            "jaw": round(f.get("open", 0.0) * 0.6, 3),
            "upper_lip": round(f.get("open", 0.0) * 0.45, 3),
            "lower_lip": round(f.get("open", 0.0) * 0.55, 3),
        })
    return out
