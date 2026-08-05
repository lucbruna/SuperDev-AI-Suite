"""Subtitle Export SRT — writes SubRip (.srt) files."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_subtitles.subtitle_timeline import SubtitleCue, to_timestamp


def export(cues: list[SubtitleCue], path: str | Path) -> dict[str, Any]:
    """Write cues to an SRT file; returns file metadata."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for i, cue in enumerate(cues, start=1):
        lines.append(str(i))
        lines.append(f"{to_timestamp(cue.start)} --> {to_timestamp(cue.end)}")
        lines.append(cue.text.replace("\\n", "\n").replace("|", "\n"))
        lines.append("")
    content = "\n".join(lines)
    out.write_text(content, encoding="utf-8")
    return {"file_path": str(out), "format": "srt", "cues": len(cues),
            "bytes": out.stat().st_size}


def read(path: str | Path) -> list[dict[str, Any]]:
    """Parse an SRT file back into dict cues."""
    from modules.ai_video_studio.ai_subtitles.subtitle_export_vtt import parse_timestamp

    text = Path(path).read_text(encoding="utf-8")
    cues: list[dict[str, Any]] = []
    blocks = text.strip().split("\n\n")
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        timing = next((ln for ln in lines if "-->" in ln), None)
        if not timing:
            continue
        start_part, end_part = timing.split("-->")
        try:
            start = parse_timestamp(start_part.strip(), sep=",")
            end = parse_timestamp(end_part.strip(), sep=",")
        except ValueError:
            continue
        text_lines = [ln for ln in lines if "-->" not in ln and not ln.isdigit()]
        cues.append({"index": len(cues) + 1, "start": start, "end": end,
                     "text": " ".join(text_lines)})
    return cues
