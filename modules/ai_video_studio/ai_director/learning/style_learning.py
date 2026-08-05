"""Style learning — learns preferred visual styles over time."""
from __future__ import annotations



class StyleLearning:
    """Tracks style preferences from feedback."""

    def __init__(self) -> None:
        self._counts: dict[str, int] = {}

    def record(self, style: str) -> None:
        self._counts[style] = self._counts.get(style, 0) + 1

    def favorite(self) -> str:
        if not self._counts:
            return "documentary"
        return max(self._counts, key=lambda style: self._counts[style])


_style_learning: StyleLearning | None = None


def get_style_learning() -> StyleLearning:
    global _style_learning
    if _style_learning is None:
        _style_learning = StyleLearning()
    return _style_learning
