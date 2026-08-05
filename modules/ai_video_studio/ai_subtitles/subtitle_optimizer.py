"""Subtitle Optimizer — merges/splits cues for comfortable reading."""
from __future__ import annotations

from modules.ai_video_studio.ai_subtitles.subtitle_timeline import SubtitleCue
from modules.ai_video_studio.ai_subtitles.subtitle_generator import MIN_CUE_SECONDS, MAX_CUE_SECONDS


def optimize(cues: list[SubtitleCue], *, max_chars: int = 42,
             max_seconds: float = MAX_CUE_SECONDS) -> list[SubtitleCue]:
    """Merge very short cues and clamp over-long ones."""
    merged: list[SubtitleCue] = []
    for cue in cues:
        if merged and _should_merge(merged[-1], cue, max_chars):
            prev = merged.pop()
            merged.append(SubtitleCue(
                index=prev.index, start=prev.start, end=cue.end,
                text=f"{prev.text} {cue.text}".strip(),
            ))
        else:
            merged.append(cue)

    out: list[SubtitleCue] = []
    for i, cue in enumerate(merged):
        duration = cue.end - cue.start
        if duration > max_seconds:
            # Split long cues proportionally by reading speed.
            chunks = cue.text.split(" ")
            if len(chunks) < 2:
                out.append(SubtitleCue(i + 1, cue.start, cue.end, cue.text))
                continue
            half = len(chunks) // 2
            mid = cue.start + (len(" ".join(chunks[:half])) / len(cue.text)) * duration
            out.append(SubtitleCue(i + 1, cue.start, mid, " ".join(chunks[:half])))
            out.append(SubtitleCue(i + 2, mid, cue.end, " ".join(chunks[half:])))
        else:
            out.append(SubtitleCue(i + 1, cue.start, cue.end, cue.text))
    return out


def _should_merge(prev: SubtitleCue, nxt: SubtitleCue, max_chars: int) -> bool:
    if prev.end - prev.start < MIN_CUE_SECONDS:
        joined = f"{prev.text} {nxt.text}".strip()
        if len(joined) <= max_chars:
            return True
    return False
