"""Subtitle track manager — cues, validation and SRT/VTT export.

Cues live on the timeline's subtitle list; helpers validate overlaps, look up
the active cue at a time, and export real SubRip (.srt) files.
"""
from __future__ import annotations

from typing import Any
from pathlib import Path

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.editor_common import make_logger

logger = make_logger("editor.subtitles")


def _fmt_srt(t: float) -> str:
    ms = int(round(t * 1000))
    h, rem = divmod(ms, 3600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


class SubtitleTrackManager:
    def __init__(self, timeline: Any) -> None:
        self.timeline = timeline

    def add(self, start: float, end: float, text: str) -> dict[str, Any]:
        if end <= start:
            raise ValidationError("Subtitle end must be after start", field="subtitle")
        for cue in self.timeline.subtitles:
            if start < cue["end"] and end > cue["start"]:
                raise ValidationError("Subtitle overlaps another cue", field="subtitle")
        return self.timeline.add_subtitle(start, end, text)

    def remove(self, cue_id: str) -> bool:
        before = len(self.timeline.subtitles)
        self.timeline.subtitles = [c for c in self.timeline.subtitles if c.get("id") != cue_id]
        return len(self.timeline.subtitles) != before

    def active_at(self, time: float) -> str:
        return self.timeline.subtitle_at(time)

    def export_srt(self, output_path: str | Path) -> str:
        """Write a real SubRip file; returns the output path."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        lines: list[str] = []
        for i, cue in enumerate(sorted(self.timeline.subtitles, key=lambda c: c["start"]), start=1):
            lines.append(f"{i}\n{_fmt_srt(cue['start'])} --> {_fmt_srt(cue['end'])}\n{cue['text']}\n")
        out.write_text("\n".join(lines), encoding="utf-8")
        logger.info("exported %d subtitles -> %s", len(self.timeline.subtitles), out)
        return str(out)
