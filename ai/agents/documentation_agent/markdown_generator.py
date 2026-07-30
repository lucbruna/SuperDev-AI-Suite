from __future__ import annotations

from typing import Any


class MarkdownGenerator:
    """Generates Markdown documentation from sections."""

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

    @property
    def section_count(self) -> int:
        return len(self._sections)

    def generate_markdown(self, content: str = "") -> str:
        if content:
            return content
        lines: list[str] = []
        for title, body in self._sections.items():
            lines.append(f"# {title}")
            lines.append("")
            lines.append(body)
            lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "sections": {k: v for k, v in self._sections.items()},
            "section_count": self.section_count,
        }
