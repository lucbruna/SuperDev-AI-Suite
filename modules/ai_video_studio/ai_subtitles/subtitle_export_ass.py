"""Subtitle Export ASS — writes Advanced SubStation Alpha (.ass) files.

Real ASS: style definitions, Script Info, and per-cue override tags
(animation, colour, karaoke) rendered by mpv/VLC and most editors.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_subtitles.subtitle_timeline import SubtitleCue, to_timestamp
from modules.ai_video_studio.ai_subtitles.subtitle_styling import style_names, to_ass_style_line


def export(cues: list[SubtitleCue], path: str | Path, *, styles: list[str] | None = None,
           animated: bool = False) -> dict[str, Any]:
    """Write cues to an ASS file (optionally with \\fad animation)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    used_styles = styles or sorted({c.style for c in cues} | {"default"})
    used_styles = [s for s in used_styles if s in style_names()] or ["default"]

    header = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        *(to_ass_style_line(s) for s in used_styles),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    event_lines: list[str] = []
    for i, cue in enumerate(cues, start=1):
        style = cue.style if cue.style in used_styles else "default"
        anim = "\\fad(200,200)" if animated else ""
        text = cue.text.replace("\n", "\\N")
        event_lines.append(
            f"Dialogue: 0,{to_timestamp(cue.start, sep=':')},{to_timestamp(cue.end, sep=':')},"
            f"{style},,0,0,0,,{anim}{text}"
        )
    out.write_text("\n".join(header + event_lines), encoding="utf-8")
    return {"file_path": str(out), "format": "ass", "cues": len(cues),
            "styles": used_styles, "bytes": out.stat().st_size}
