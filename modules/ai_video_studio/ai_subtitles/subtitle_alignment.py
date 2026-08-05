"""Subtitle Alignment — snaps cues to actual speech activity.

When speech segmentation is available (VAD / recognition timings), cues are
scaled to the detected segments so subtitles match what is really spoken.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_subtitles.subtitle_timeline import SubtitleCue


def align_to_segments(cues: list[SubtitleCue], segments: list[dict]) -> list[SubtitleCue]:
    """``segments``: list of ``{start, end}`` — distribute cues over speech spans."""
    if not segments:
        return cues
    total_speech = sum(s["end"] - s["start"] for s in segments)
    if total_speech <= 0:
        return cues
    aligned: list[SubtitleCue] = []
    t = 0.0
    for i, cue in enumerate(cues):
        duration = cue.end - cue.start
        aligned.append(SubtitleCue(i + 1, t, t + duration, cue.text, cue.style))
        t += duration
    # Map the aligned timeline onto the speech segments proportionally.
    final: list[SubtitleCue] = []
    aligned_len = t if t > 0 else 1.0
    for cue in aligned:
        start_ratio = cue.start / aligned_len
        end_ratio = cue.end / aligned_len
        final.append(SubtitleCue(
            cue.index,
            _position_in_segments(segments, start_ratio),
            _position_in_segments(segments, end_ratio),
            cue.text, cue.style,
        ))
    return final


def _position_in_segments(segments: list[dict], ratio: float) -> float:
    total = sum(s["end"] - s["start"] for s in segments)
    target = total * ratio
    acc = 0.0
    for s in segments:
        span = s["end"] - s["start"]
        if target <= acc + span:
            return s["start"] + (target - acc)
        acc += span
    return segments[-1]["end"] if segments else 0.0
