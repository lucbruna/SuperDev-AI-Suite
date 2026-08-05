"""Agriculture AI Connector — facade over the agriculture generators."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.agriculture_ai.crop_video_generator import (
    get_crop_video_generator,
)
from modules.ai_video_studio.integration.agriculture_ai.drone_video_generator import (
    get_drone_video_generator,
)
from modules.ai_video_studio.integration.agriculture_ai.harvest_reports import (
    get_harvest_report_generator,
)
from modules.ai_video_studio.integration.agriculture_ai.irrigation_visualizer import (
    get_irrigation_visualizer,
)
from modules.ai_video_studio.integration.agriculture_ai.livestock_video_generator import (
    get_livestock_video_generator,
)
from modules.ai_video_studio.integration.agriculture_ai.plantation_storyboard import (
    get_plantation_storyboard,
)
from modules.ai_video_studio.integration.agriculture_ai.weather_video_builder import (
    get_weather_video_builder,
)
from modules.ai_video_studio.integration.connector_base import DomainConnector


class AgricultureConnector(DomainConnector):
    """Generates agriculture-domain video briefs."""

    domain = "agriculture"
    description = "Crop/livestock/drone videos, plantation storyboards, weather videos, harvest reports and irrigation visuals"

    def __init__(self) -> None:
        super().__init__()
        self._register("crop_video", self._crop)
        self._register("livestock_video", self._livestock)
        self._register("drone_video", self._drone)
        self._register("plantation_storyboard", self._storyboard)
        self._register("weather_video", self._weather)
        self._register("harvest_report", self._harvest)
        self._register("irrigation_visual", self._irrigation)

    def _crop(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_crop_video_generator().generate(**data)

    def _livestock(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_livestock_video_generator().generate(**data)

    def _drone(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_drone_video_generator().generate(**data)

    def _storyboard(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_plantation_storyboard().build(**data)

    def _weather(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_weather_video_builder().build(**data)

    def _harvest(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_harvest_report_generator().generate(**data)

    def _irrigation(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_irrigation_visualizer().build(**data)


_agriculture_connector: AgricultureConnector | None = None


def get_agriculture_connector() -> AgricultureConnector:
    global _agriculture_connector
    if _agriculture_connector is None:
        _agriculture_connector = AgricultureConnector()
    return _agriculture_connector
