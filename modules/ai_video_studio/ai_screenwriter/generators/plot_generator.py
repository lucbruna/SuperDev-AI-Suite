"""Plot generator — outlines plot beats for a script."""
from __future__ import annotations

from typing import Any


class PlotGenerator:
    """Generates plot beats for narrative scripts."""

    BEATS = ["inciting_incident", "rising_action", "climax", "falling_action", "resolution"]

    def generate(self, topic: str) -> dict[str, Any]:
        return {
            "beats": self.BEATS,
            "climax": f"O momento decisivo sobre {topic.lower() or 'o tema'}.",
        }


_plot_generator: PlotGenerator | None = None


def get_plot_generator() -> PlotGenerator:
    global _plot_generator
    if _plot_generator is None:
        _plot_generator = PlotGenerator()
    return _plot_generator
