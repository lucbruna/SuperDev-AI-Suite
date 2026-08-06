"""Report generator: deterministic Markdown reports."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ReportSection:
    """A named section with bullet content."""

    title: str
    lines: list[str]


class ReportGenerator:
    """Builds a Markdown report from named sections."""

    def render(self, title: str, sections: list[ReportSection]) -> str:
        parts = [f"# {title}", ""]
        for section in sections:
            parts.append(f"## {section.title}")
            parts.append("")
            for line in section.lines:
                parts.append(f"- {line}")
            parts.append("")
        return "\n".join(parts)

    def render_payload(
        self, title: str, data: dict[str, Any]
    ) -> str:
        sections: list[ReportSection] = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines = [f"{k}: {v}" for k, v in value.items()]
            elif isinstance(value, list):
                lines = [str(item) for item in value]
            else:
                lines = [str(value)]
            sections.append(ReportSection(title=key, lines=lines))
        return self.render(title, sections)
