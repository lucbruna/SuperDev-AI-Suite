from __future__ import annotations

from typing import Any


class ArchitectureDocument:
    """Generates architecture documentation from sections."""

    def __init__(self) -> None:
        self._sections: dict[str, str] = {}

    def add_section(self, title: str, content: str) -> str:
        self._sections[title] = content
        return title

    def get_section(self, title: str) -> str | None:
        return self._sections.get(title)

    def remove_section(self, title: str) -> bool:
        if title in self._sections:
            del self._sections[title]
            return True
        return False

    def generate_report(self) -> str:
        if not self._sections:
            return "# Architecture Document\n\n*(no sections)*"

        lines: list[str] = []
        lines.append("# Architecture Document")
        lines.append("")
        for title, content in self._sections.items():
            lines.append(f"## {title}")
            lines.append("")
            lines.append(content)
            lines.append("")
        return "\n".join(lines)

    @property
    def section_count(self) -> int:
        return len(self._sections)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sections": dict(self._sections),
            "section_count": self.section_count,
        }
