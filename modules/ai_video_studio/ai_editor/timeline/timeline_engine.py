"""Professional timeline — the multi-track model of the editor.

Supports video/audio/subtitle/effect/transition/marker tracks, per-clip
properties (speed, opacity, transform, effects, volume keyframes), markers,
subtitles and transitions between adjacent clips. All mutations validate and
keep the timeline consistent so the renderer can rely on it.
"""
from __future__ import annotations

import uuid
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.timeline")

TRACK_TYPES = {"video", "audio", "subtitle", "effect", "transition", "marker"}


class ProfessionalTimeline:
    """A timeline of clips organised in typed, ordered tracks."""

    def __init__(self, *, fps: int = 24) -> None:
        self.fps = int(fps)
        self.tracks: dict[str, dict[str, Any]] = {}
        self.clips: list[dict[str, Any]] = []
        self.markers: list[dict[str, Any]] = []
        self.subtitles: list[dict[str, Any]] = []
        self.transitions: list[dict[str, Any]] = []

    # ── Tracks ───────────────────────────────────────────────────
    def add_track(self, name: str, track_type: str = "video") -> dict[str, Any]:
        if track_type not in TRACK_TYPES:
            raise ValidationError(
                f"Unknown track type '{track_type}' (expected one of {sorted(TRACK_TYPES)})",
                field="track_type",
            )
        if name in self.tracks:
            raise ValidationError(f"Track '{name}' already exists", field="track")
        track = {"id": name, "type": track_type, "muted": False, "locked": False, "hidden": False}
        self.tracks[name] = track
        return track

    def ensure_track(self, name: str, track_type: str = "video") -> dict[str, Any]:
        return self.tracks.get(name) or self.add_track(name, track_type)

    def remove_track(self, name: str) -> bool:
        if name not in self.tracks:
            return False
        self.clips = [c for c in self.clips if c.get("track") != name]
        del self.tracks[name]
        return True

    def set_track_flag(self, name: str, flag: str, value: bool) -> dict[str, Any]:
        if name not in self.tracks:
            raise ValidationError(f"Track '{name}' not found", field="track")
        if flag not in {"muted", "locked", "hidden"}:
            raise ValidationError(f"Unknown track flag '{flag}'", field="flag")
        self.tracks[name][flag] = bool(value)
        return self.tracks[name]

    # ── Clips ────────────────────────────────────────────────────
    def add_clip(self, clip: dict[str, Any], track: str = "video") -> dict[str, Any]:
        start = clip.get("start")
        end = clip.get("end")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise ValidationError("Clip must have numeric start and end", field="clip")
        if end <= start:
            raise ValidationError("Clip end must be after start", field="clip")
        if start < 0:
            raise ValidationError("Clip start cannot be negative", field="clip")
        self.ensure_track(track, "video" if track != "audio" else "audio")
        clip.setdefault("id", f"clip_{uuid.uuid4().hex[:8]}")
        clip.setdefault("source", clip.get("source") or "generated")
        clip.setdefault("source_in", 0.0)
        clip.setdefault("speed", 1.0)
        clip.setdefault("opacity", 1.0)
        clip.setdefault("volume", 1.0)
        clip.setdefault("transform", {"x": 0, "y": 0, "scale": 1.0, "rotation": 0.0})
        clip.setdefault("effects", [])
        clip.setdefault("volume_keyframes", {})
        clip.setdefault("track", track)
        self.clips.append(clip)
        return clip

    def get_clip(self, clip_id: str) -> dict[str, Any]:
        for clip in self.clips:
            if clip.get("id") == clip_id:
                return clip
        raise ValidationError(f"Clip '{clip_id}' not found", field="clip_id")

    def remove_clip(self, clip_id: str) -> dict[str, Any] | None:
        removed = self.get_clip(clip_id) if any(c.get("id") == clip_id for c in self.clips) else None
        self.clips = [c for c in self.clips if c.get("id") != clip_id]
        self.transitions = [t for t in self.transitions if clip_id not in (t.get("a"), t.get("b"))]
        return removed

    def move_clip(self, clip_id: str, start: float, track: str | None = None) -> dict[str, Any]:
        clip = self.get_clip(clip_id)
        duration = clip["end"] - clip["start"]
        if start < 0:
            raise ValidationError("Clip start cannot be negative", field="clip")
        clip["start"] = start
        clip["end"] = start + duration
        if track is not None:
            clip["track"] = track
        return clip

    def set_clip_volume(self, clip_id: str, volume: float, t: float = 0.0) -> dict[str, Any]:
        clip = self.get_clip(clip_id)
        if volume < 0:
            raise ValidationError("Volume cannot be negative", field="volume")
        if t <= 0:
            clip["volume"] = volume
        else:
            clip["volume_keyframes"][str(round(t, 3))] = volume
        return clip

    def add_clip_effect(self, clip_id: str, effect: str, params: dict[str, Any]) -> dict[str, Any]:
        clip = self.get_clip(clip_id)
        effect_id = f"fx_{uuid.uuid4().hex[:8]}"
        entry = {"id": effect_id, "name": effect, "params": dict(params)}
        clip.setdefault("effects", []).append(entry)
        return entry

    # ── Markers / subtitles / transitions ────────────────────────
    def add_marker(self, time: float, label: str = "", color: str = "yellow") -> dict[str, Any]:
        if time < 0:
            raise ValidationError("Marker time cannot be negative", field="time")
        marker = {"id": f"mk_{uuid.uuid4().hex[:8]}", "time": time, "label": label, "color": color}
        self.markers.append(marker)
        self.markers.sort(key=lambda m: m["time"])
        return marker

    def add_subtitle(self, start: float, end: float, text: str) -> dict[str, Any]:
        cue = {"id": f"st_{uuid.uuid4().hex[:8]}", "start": start, "end": end, "text": text}
        self.subtitles.append(cue)
        self.subtitles.sort(key=lambda c: c["start"])
        return cue

    def set_transition(self, clip_a_id: str, clip_b_id: str, transition: str, duration: float) -> dict[str, Any]:
        if duration <= 0:
            raise ValidationError("Transition duration must be positive", field="duration")
        entry = {"a": clip_a_id, "b": clip_b_id, "name": transition, "duration": duration}
        self.transitions = [t for t in self.transitions if not (t.get("a") == clip_a_id and t.get("b") == clip_b_id)]
        self.transitions.append(entry)
        return entry

    # ── Queries ──────────────────────────────────────────────────
    def clips_on(self, track: str) -> list[dict[str, Any]]:
        return sorted((c for c in self.clips if c.get("track") == track), key=lambda c: c["start"])

    def clips_at(self, time: float, track_type: str | None = None) -> list[dict[str, Any]]:
        result = [c for c in self.clips if c["start"] <= time < c["end"]]
        if track_type:
            result = [c for c in result if (self.tracks.get(c.get("track", "")) or {}).get("type") == track_type]
        return result

    def subtitle_at(self, time: float) -> str:
        for cue in self.subtitles:
            if cue["start"] <= time < cue["end"]:
                return cue["text"]
        return ""

    def duration(self) -> float:
        return max((c["end"] for c in self.clips), default=0.0)

    def clip_count(self) -> int:
        return len(self.clips)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fps": self.fps,
            "tracks": {k: dict(v) for k, v in self.tracks.items()},
            "clips": [dict(c) for c in self.clips],
            "markers": [dict(m) for m in self.markers],
            "subtitles": [dict(s) for s in self.subtitles],
            "transitions": [dict(t) for t in self.transitions],
            "duration": self.duration(),
        }

    def load_dict(self, data: dict[str, Any]) -> None:
        self.fps = int(data.get("fps", 24))
        self.tracks = {k: dict(v) for k, v in data.get("tracks", {}).items()}
        self.clips = [dict(c) for c in data.get("clips", [])]
        self.markers = [dict(m) for m in data.get("markers", [])]
        self.subtitles = [dict(s) for s in data.get("subtitles", [])]
        self.transitions = [dict(t) for t in data.get("transitions", [])]
