"""Deterministic session and summary report generation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from modules.autonomous_developer.core.context import DeveloperContext

__all__ = ["Report", "ReportGenerator", "ReportSection"]


@dataclass(slots=True)
class ReportSection:
    """A heading/body pair inside a report."""

    heading: str
    body: str


@dataclass(slots=True)
class Report:
    """A report with a title and ordered sections, rendered to markdown."""

    title: str
    sections: list[ReportSection] = field(default_factory=list)

    def to_markdown(self) -> str:
        parts = [f"# {self.title}"]
        for section in self.sections:
            parts.append(f"## {section.heading}")
            parts.append(section.body)
        return "\n\n".join(parts) + "\n"


class ReportGenerator:
    """Builds reports from context stats and artifacts."""

    def session_report(self, ctx: DeveloperContext, goal: str = "") -> Report:
        sections: list[ReportSection] = []
        if goal:
            sections.append(ReportSection("Goal", goal))
        stats_lines = [
            f"- {key}: {value}" for key, value in sorted(ctx.stats.items())
        ]
        sections.append(
            ReportSection("Stats", "\n".join(stats_lines) if stats_lines else "_none_")
        )
        artifact_lines = [
            f"- {key}: {type(value).__name__}"
            for key, value in sorted(ctx.artifacts.items())
        ]
        sections.append(
            ReportSection(
                "Artifacts",
                "\n".join(artifact_lines) if artifact_lines else "_none_",
            )
        )
        return Report(title="Session Report", sections=sections)

    def summary_report(self, ctx: DeveloperContext) -> Report:
        return Report(
            title="Summary Report",
            sections=[
                ReportSection("Stats", f"Recorded {len(ctx.stats)} stat(s)."),
                ReportSection("Artifacts", f"Produced {len(ctx.artifacts)} artifact(s)."),
            ],
        )

    def run(self, ctx: DeveloperContext, goal: str, **kwargs: Any) -> Report:
        """Generate a session report and publish a report.generated event."""
        report = self.session_report(ctx, goal)
        ctx.record("report_sections", len(report.sections))
        ctx.publish("report.generated", {"title": report.title})
        return report
