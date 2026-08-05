"""Audio track manager — audio clips, automation and a simple mixdown.

Audio clips carry an optional ``samples`` array (float mono/stereo at the
timeline fps) plus volume automation keyframes. ``mixdown(duration)`` returns a
real float array mixing all audible audio clips with their keyframed volume.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from modules.ai_video_studio.editor_common import lerp, make_logger

logger = make_logger("editor.audio")


class AudioTrackManager:
    def __init__(self, timeline: Any, sample_rate: int = 44100) -> None:
        self.timeline = timeline
        self.sample_rate = sample_rate

    def add_audio_clip(self, clip: dict[str, Any], track: str = "audio") -> dict[str, Any]:
        return self.timeline.add_clip(clip, track=track)

    def set_volume_keyframe(self, clip_id: str, time: float, volume: float) -> dict[str, Any]:
        clip = self.timeline.get_clip(clip_id)
        if volume < 0:
            raise ValueError("volume must be >= 0")
        clip.setdefault("volume_keyframes", {})[str(round(time, 3))] = volume
        return clip

    def volume_at(self, clip: dict[str, Any], time: float) -> float:
        """Interpolate the clip volume at ``time`` (seconds into the clip)."""
        keyframes = sorted((float(k), v) for k, v in clip.get("volume_keyframes", {}).items())
        if not keyframes:
            return float(clip.get("volume", 1.0))
        if time <= keyframes[0][0]:
            return keyframes[0][1]
        if time >= keyframes[-1][0]:
            return keyframes[-1][1]
        for (t0, v0), (t1, v1) in zip(keyframes, keyframes[1:]):
            if t0 <= time <= t1:
                return lerp(v0, v1, (time - t0) / max(1e-9, t1 - t0))
        return float(clip.get("volume", 1.0))

    def mixdown(self, duration: float | None = None) -> np.ndarray:
        """Mix all audible audio clips into a single float array (mono)."""
        duration = duration if duration is not None else self.timeline.duration()
        frames = max(1, int(duration * self.sample_rate))
        mix = np.zeros(frames, dtype=np.float32)
        audible = [t for t, tr in self.timeline.tracks.items() if tr.get("type") == "audio" and not tr.get("muted")]
        for clip in self.timeline.clips:
            if clip.get("track") not in audible or "samples" not in clip:
                continue
            samples = np.asarray(clip["samples"], dtype=np.float32)
            if samples.ndim == 2:
                samples = samples.mean(axis=1)
            start = int(clip["start"] * self.sample_rate)
            for i in range(min(len(samples), frames - start)):
                t = (i / self.sample_rate)
                mix[start + i] += samples[i] * self.volume_at(clip, t)
        return mix
