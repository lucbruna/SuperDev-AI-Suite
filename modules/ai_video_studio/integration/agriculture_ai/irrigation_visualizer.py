"""Irrigation Visualizer — water-need summary and video brief."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class IrrigationVisualizer:
    """Builds irrigation guidance videos from soil/ET data."""

    def build(self, *, crop: str = "wheat", et_mm: float = 4.5, soil_moisture: float = 42.0,
              voice: str = "default") -> dict[str, Any]:
        deficit = max(0.0, round(et_mm - soil_moisture / 10.0, 1))
        need = "high" if deficit > 3.0 else ("moderate" if deficit > 1.0 else "low")
        title = f"{crop.title()} irrigation — {need} need"
        scenes = [
            f"Irrigation status for {crop}: evapotranspiration {et_mm:g} mm/day.",
            f"Current soil moisture {soil_moisture:g}% with a deficit of {deficit:g} mm.",
            f"Water need is {need} — adjust the schedule accordingly.",
            "Use soil sensors to confirm before the next irrigation event.",
        ]
        brief = build_brief("agriculture", title, scenes, voice=voice,
                            crop=crop, need=need).to_dict()
        brief["meta"]["deficit_mm"] = deficit
        return brief


_irrigation_visualizer: IrrigationVisualizer | None = None


def get_irrigation_visualizer() -> IrrigationVisualizer:
    global _irrigation_visualizer
    if _irrigation_visualizer is None:
        _irrigation_visualizer = IrrigationVisualizer()
    return _irrigation_visualizer
