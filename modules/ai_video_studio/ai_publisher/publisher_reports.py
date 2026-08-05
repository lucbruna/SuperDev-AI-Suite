"""Publisher Reports — generates summary reports for publishing activity (Volume 7)."""
from __future__ import annotations

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PublisherReports:
    """Assemble human-readable and structured publish reports."""

    def _as_rows(self, statistics: dict) -> list[tuple[str, str, str]]:
        rows = []
        for platform, metrics in statistics.items():
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    rows.append((platform, key, str(value)))
        return rows

    def summary(self, *, statistics: dict) -> dict:
        """Build a structured report from per-platform statistics."""
        totals = {k: 0 for k in ["views", "likes", "comments", "shares"]}
        platform_count = 0
        for metrics in statistics.values():
            platform_count += 1
            for key in totals:
                totals[key] += metrics.get(key, 0)
        return {
            "generated_at": datetime.now().isoformat(),
            "platforms": platform_count,
            "totals": totals,
        }

    def markdown(self, *, statistics: dict) -> str:
        """Render a markdown report from per-platform statistics."""
        lines = ["# Publisher Report", "", f"Generated: {datetime.now().isoformat()}", ""]
        for platform, metrics in sorted(statistics.items()):
            lines.append(f"## {platform.title()}")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    lines.append(f"- {key}: {value:,.0f}" if isinstance(value, float) and value != int(value) else f"- {key}: {value}")
            lines.append("")
        return "\n".join(lines)

    def stats(self) -> dict[str, int]:
        return {"report_types": 2}


_REPORTS: PublisherReports | None = None


def get_publisher_reports() -> PublisherReports:
    """Get the module-level singleton report generator."""
    global _REPORTS
    if _REPORTS is None:
        _REPORTS = PublisherReports()
    return _REPORTS
