"""Effect track manager — effect instances and parameter keyframes.

Effects are attached to clips (``clip["effects"]``) or to whole tracks
(``track["effects"]``). Parameters can be animated with keyframes; helpers
evaluate a parameter's value at a given time by linear interpolation.
"""
from __future__ import annotations

import uuid
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import lerp, make_logger

logger = make_logger("editor.effects")


class EffectTrackManager:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def add_effect(self, clip_id: str, name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.timeline.add_clip_effect(clip_id, name, params or {})

    def remove_effect(self, clip_id: str, effect_id: str) -> bool:
        clip = self.timeline.get_clip(clip_id)
        before = len(clip.get("effects", []))
        clip["effects"] = [e for e in clip.get("effects", []) if e.get("id") != effect_id]
        return len(clip["effects"]) != before

    def set_keyframe(self, clip_id: str, effect_id: str, param: str, time: float, value: float) -> dict[str, Any]:
        clip = self.timeline.get_clip(clip_id)
        for effect in clip.get("effects", []):
            if effect.get("id") == effect_id:
                kf = effect.setdefault("keyframes", {})
                kf.setdefault(param, {})[str(round(time, 3))] = value
                return effect
        raise ValidationError(f"Effect '{effect_id}' not found on clip", field="effect_id")

    def param_at(self, effect: dict[str, Any], param: str, time: float, default: float = 0.0) -> float:
        """Evaluate a keyframed parameter at ``time`` (seconds)."""
        kf = sorted((float(k), v) for k, v in effect.get("keyframes", {}).get(param, {}).items())
        if not kf:
            return float(effect.get("params", {}).get(param, default))
        if time <= kf[0][0]:
            return kf[0][1]
        if time >= kf[-1][0]:
            return kf[-1][1]
        for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
            if t0 <= time <= t1:
                return lerp(v0, v1, (time - t0) / max(1e-9, t1 - t0))
        return float(effect.get("params", {}).get(param, default))
