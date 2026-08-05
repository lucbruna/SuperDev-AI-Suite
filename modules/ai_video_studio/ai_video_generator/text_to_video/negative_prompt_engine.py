"""Negative prompt engine — build and maintain negative prompt lists."""
from __future__ import annotations

_DEFAULTS = [
    "blurry",
    "distorted",
    "low quality",
    "watermark",
    "text artifacts",
    "extra limbs",
    "deformed face",
]


class NegativePromptEngine:
    """Composes negative prompts from defaults plus user extras."""

    def __init__(self) -> None:
        self._custom: dict[str, list[str]] = {}

    def compose(self, *, style: str | None = None, extras: list[str] | None = None) -> list[str]:
        negative = list(_DEFAULTS)
        if style:
            negative.extend(self._custom.get(style, []))
        if extras:
            negative.extend(extras)
        return list(dict.fromkeys(negative))

    def add_style_negative(self, style: str, phrase: str) -> None:
        self._custom.setdefault(style, []).append(phrase)

    def join(self, negatives: list[str]) -> str:
        return ", ".join(negatives)
