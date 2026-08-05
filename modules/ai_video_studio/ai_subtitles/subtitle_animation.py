"""Subtitle Animation — generates ASS animation override tags.

All tags are real ASS Override Tags (\\fad, \\move, \\fscx, \\k, ...) that
players like mpv/VLC render natively.
"""
from __future__ import annotations


def fade_in_out(fade_in: float = 0.2, fade_out: float = 0.2) -> str:
    return f"\\fad({int(fade_in * 1000)},{int(fade_out * 1000)})"


def slide_up(offset: int = 20, duration: float = 0.3) -> str:
    return f"\\move(0,{offset},0,0,0,{int(duration * 1000)})"


def zoom_pulse(scale: float = 1.2) -> str:
    return f"\\fscx{scale}\\fscy{scale}"


def color_karaoke(start_color: str = "&H0000FFFF", main_color: str = "&H00FFFFFF") -> str:
    return f"\\1c{start_color}\\t(0,0,{main_color})"


def italic() -> str:
    return "\\i1"


def bold() -> str:
    return "\\b1"
