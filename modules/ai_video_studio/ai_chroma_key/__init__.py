"""Chroma key subsystem — green/blue screen removal and background replace."""
from __future__ import annotations

from .chroma_engine import ChromaKeyEngine
from .green_screen import key_green_screen
from .blue_screen import key_blue_screen
from .background_replacement import replace_background
from .object_extraction import extract_object

__all__ = [
    "ChromaKeyEngine",
    "key_green_screen",
    "key_blue_screen",
    "replace_background",
    "extract_object",
]

engine = ChromaKeyEngine()
