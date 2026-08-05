"""Expression Controller — combines mouth and eye features per frame."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_lip_sync.smile_controller import smile_curve


def expression_curve(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-frame ``{smile, surprise, neutral}`` blend weights."""
    smiles = {f["frame"]: f["value"] for f in smile_curve(timeline)}
    out: list[dict[str, Any]] = []
    for f in timeline:
        smile = smiles.get(f.get("frame"), 0.0)
        open_ = f.get("open", 0.0)
        surprise = min(1.0, open_ * 1.2) if open_ > 0.7 else 0.0
        neutral = max(0.0, 1.0 - smile - surprise * 0.5)
        out.append({
            "frame": f.get("frame"), "time": f.get("time"),
            "smile": round(smile, 3), "surprise": round(surprise, 3),
            "neutral": round(neutral, 3),
        })
    return out
