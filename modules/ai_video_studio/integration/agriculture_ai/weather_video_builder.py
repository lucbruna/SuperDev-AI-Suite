"""Weather Video Builder — briefs driven by forecast conditions."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief

_CONDITIONS: dict[str, str] = {
    "frost": "protect crops from frost damage tonight",
    "drought": "irrigation priorities during the dry spell",
    "rain": "field operations during the rain window",
    "heat": "heat stress management for crops and livestock",
}


class WeatherVideoBuilder:
    """Builds weather-alert narration scripts."""

    def build(self, *, condition: str = "frost", region: str = "south",
              voice: str = "default") -> dict[str, Any]:
        condition = condition if condition in _CONDITIONS else "frost"
        title = f"Weather alert — {condition} in {region}"
        scenes = [
            f"Weather alert for {region}: {_CONDITIONS[condition]}.",
            "Check local forecasts and field conditions before acting.",
            "Recommended actions are listed in the checklist below.",
            f"Stay updated — this {condition} window lasts a few days.",
        ]
        return build_brief("agriculture", title, scenes, voice=voice,
                           condition=condition, region=region).to_dict()


_weather_video_builder: WeatherVideoBuilder | None = None


def get_weather_video_builder() -> WeatherVideoBuilder:
    global _weather_video_builder
    if _weather_video_builder is None:
        _weather_video_builder = WeatherVideoBuilder()
    return _weather_video_builder
