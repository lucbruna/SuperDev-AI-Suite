"""Harvest Reports — computes harvest statistics and builds a report brief."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class HarvestReportGenerator:
    """Aggregates per-field harvest data into a summary video brief."""

    def generate(self, *, crop: str = "corn", fields: list[dict[str, Any]] | None = None,
                 voice: str = "default") -> dict[str, Any]:
        fields = fields or [
            {"name": "field_a", "area_ha": 50.0, "yield_t": 9.2},
            {"name": "field_b", "area_ha": 30.0, "yield_t": 7.8},
        ]
        total_area = sum(float(f.get("area_ha", 0)) for f in fields)
        total_yield = sum(float(f.get("yield_t", 0)) for f in fields)
        avg_yield = total_yield / total_area if total_area else 0.0
        best = max(fields, key=lambda f: f.get("yield_t", 0))

        scenes = [
            f"Harvest summary for {crop}: {len(fields)} fields, {total_area:g} ha.",
            f"Total production {total_yield:g} tons at an average of {avg_yield:.2f} t/ha.",
            f"Best performer: {best['name']} with {best['yield_t']:g} tons.",
            "Compare this cycle with last season and refine inputs.",
        ]
        brief = build_brief("agriculture", f"{crop.title()} harvest report", scenes,
                            voice=voice, crop=crop).to_dict()
        brief["meta"]["stats"] = {
            "fields": len(fields), "total_area_ha": round(total_area, 2),
            "total_yield_t": round(total_yield, 2), "avg_yield_t_ha": round(avg_yield, 2),
        }
        return brief


_harvest_report_generator: HarvestReportGenerator | None = None


def get_harvest_report_generator() -> HarvestReportGenerator:
    global _harvest_report_generator
    if _harvest_report_generator is None:
        _harvest_report_generator = HarvestReportGenerator()
    return _harvest_report_generator
