"""Executive Reports — consolidated KPI reports for executives."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class ExecutiveReportGenerator:
    """Builds narration scripts summarizing executive KPIs."""

    def generate(self, *, title: str = "Executive summary", kpis: dict[str, float] | None = None,
                 voice: str = "default") -> dict[str, Any]:
        kpis = kpis or {"revenue": 480000, "customers": 3200, "churn": 0.04}
        headline = max(kpis, key=kpis.get)
        scenes = [
            f"{title}: {len(kpis)} KPIs reviewed.",
            f"Strongest KPI is {headline} at {kpis[headline]:g}.",
            "Trends and targets are summarized per KPI.",
            "Full detail is available in the attached report.",
        ]
        return build_brief("bi", title, scenes, voice=voice,
                           kpis={k: round(v, 4) for k, v in kpis.items()}).to_dict()


_executive_report_generator: ExecutiveReportGenerator | None = None


def get_executive_report_generator() -> ExecutiveReportGenerator:
    global _executive_report_generator
    if _executive_report_generator is None:
        _executive_report_generator = ExecutiveReportGenerator()
    return _executive_report_generator
