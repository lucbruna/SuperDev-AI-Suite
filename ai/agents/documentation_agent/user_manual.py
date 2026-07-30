from __future__ import annotations

from typing import Any


class UserManual:
    """Generates user manuals with sections and steps."""

    def __init__(self) -> None:
        self._sections: dict[str, str] = {}
        self._steps: dict[str, list[str]] = {}

    def add_section(self, title: str, content: str) -> str:
        self._sections[title] = content
        return title

    def get_section(self, title: str) -> str | None:
        return self._sections.get(title)

    @property
    def section_count(self) -> int:
        return len(self._sections)

    def add_step(self, section: str, step: str) -> str:
        if section not in self._steps:
            self._steps[section] = []
        self._steps[section].append(step)
        return step

    def generate(self) -> str:
        lines: list[str] = ["# User Manual", ""]
        for title, content in self._sections.items():
            lines.append(f"## {title}")
            lines.append(content)
            lines.append("")
            if title in self._steps and self._steps[title]:
                lines.append("### Steps")
                for i, step in enumerate(self._steps[title], 1):
                    lines.append(f"{i}. {step}")
                lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "sections": {k: v for k, v in self._sections.items()},
            "steps": {k: v for k, v in self._steps.items()},
            "section_count": self.section_count,
        }
