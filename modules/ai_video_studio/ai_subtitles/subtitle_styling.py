"""Subtitle Styling — named ASS styles used by the ASS exporter."""
from __future__ import annotations

STYLES: dict[str, dict] = {
    "default": {"fontname": "Arial", "fontsize": 22, "primary": "&H00FFFFFF",
                "outline": "&H00000000", "back": "&H96000000", "bold": 0, "outline_size": 2, "shadow": 1},
    "cinematic": {"fontname": "Georgia", "fontsize": 26, "primary": "&H00F5F0E6",
                  "outline": "&H00000000", "back": "&H80000000", "bold": 0, "outline_size": 2, "shadow": 0},
    "gaming": {"fontname": "Arial Black", "fontsize": 24, "primary": "&H00FFD700",
               "outline": "&H00000000", "back": "&H8C000000", "bold": 1, "outline_size": 3, "shadow": 2},
    "news": {"fontname": "Tahoma", "fontsize": 20, "primary": "&H00FFFFFF",
             "outline": "&H00000000", "back": "&H90000000", "bold": 0, "outline_size": 2, "shadow": 1},
    "karaoke": {"fontname": "Arial", "fontsize": 28, "primary": "&H0000FFFF",
                "outline": "&H00000000", "back": "&H96000000", "bold": 1, "outline_size": 2, "shadow": 1},
}


def get_style(name: str) -> dict:
    return dict(STYLES.get(name, STYLES["default"]))


def style_names() -> list[str]:
    return sorted(STYLES)


def to_ass_style_line(name: str) -> str:
    s = get_style(name)
    return (
        f"Style: {name},{s['fontname']},{s['fontsize']},{s['primary']},"
        f"&H00FFFFFF,&H00FFFFFF,{s['outline']},{s['back']},{s['bold']},0,0,0,"
        f"100,100,0,0,1,{s['outline_size']},{s['shadow']},2,2,10,10,1"
    )
