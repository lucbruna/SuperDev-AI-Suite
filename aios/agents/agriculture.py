"""AgricultureAgent: deterministic crop advisory and irrigation planning."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent

CROP_GUIDE: dict[str, dict[str, Any]] = {
    "corn": {"yield": "9.5 t/ha", "days": 110, "notes": "needs full sun and warm soil"},
    "soybean": {"yield": "3.2 t/ha", "days": 100, "notes": "fixes nitrogen; rotate with corn"},
    "wheat": {"yield": "5.0 t/ha", "days": 120, "notes": "cool-season crop, drought tolerant"},
    "rice": {"yield": "6.8 t/ha", "days": 130, "notes": "flooded paddy or upland"},
    "tomato": {"yield": "45 t/ha", "days": 80, "notes": "stake plants and monitor humidity"},
}


class AgricultureAgent(BaseAgent):
    def __init__(self, name: str = "agriculture", guide: dict[str, dict[str, Any]] | None = None, **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="agriculture",
            capabilities=["crop_advisory", "irrigation_planning", "yield_forecast"],
            description="Advisory for crops, irrigation and yields",
            **kwargs,
        )
        self.guide = dict(guide or CROP_GUIDE)

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        crop = input_data if isinstance(input_data, str) else str(input_data.get("crop", "corn"))
        if isinstance(input_data, dict):
            soil = input_data.get("soil") or context.get("soil", "loam")
            water = input_data.get("water_available") or context.get("water_available", "adequate")
        else:
            soil = context.get("soil", "loam")
            water = context.get("water_available", "adequate")
        guide = self.guide.get(crop.lower(), self.guide["corn"])
        irrigation = "daily" if water == "scarce" else ("weekly" if water == "adequate" else "minimal")
        return {
            "crop": crop,
            "soil": soil,
            "water_available": water,
            "recommended_irrigation": irrigation,
            "yield_estimate": guide["yield"],
            "growing_days": guide["days"],
            "notes": guide["notes"],
        }
