"""Subtitle Export VTT — writes WebVTT (.vtt) files (incl. styling)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_subtitles.subtitle_timeline import SubtitleCue, to_timestamp
from modules.ai_video_studio.ai_subtitles.subtitle_styling import get_style


def parse_timestamp(text: str, *, sep: str = ",") -> float:
    """Parse ``HH:MM:SS{sep}mmm`` to seconds; raises ValueError on bad input."""
    text = text.strip().replace(".", sep) if sep != "." else text.strip()
    try:
        h, m, rest = text.split(":")
        s, ms = rest.split(sep)
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0
    except ValueError:
        raise ValueError(f"Invalid timestamp: {text!r}") from None


def export(cues: list[SubtitleCue], path: str | Path, *, with_styles: bool = False) -> dict[str, Any]:
    """Write cues to a WebVTT file (optional inline styling)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ["WEBVTT", ""]
    if with_styles:
        style = get_style("default")
        lines.append("STYLE")
        lines.append(f"::cue {{ color: {style['primary'].replace('&H00', '#')}; }}")
        lines.append("")
    for i, cue in enumerate(cues, start=1):
        lines.append(f"{i}")
        lines.append(f"{to_timestamp(cue.start, sep='.')} --> {to_timestamp(cue.end, sep='.')}")
        lines.append(cue.text.replace("\\n", "\n").replace("|", "\n"))
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return {"file_path": str(out), "format": "vtt", "cues": len(cues),
            "bytes": out.stat().st_size}
