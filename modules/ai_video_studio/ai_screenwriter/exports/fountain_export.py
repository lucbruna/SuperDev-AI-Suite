"""Fountain export — converts a script to Fountain screenplay format."""
from __future__ import annotations

from typing import Any


class FountainExport:
    """Exports a script dict to Fountain plain-text markup."""

    def export(self, script: dict[str, Any]) -> str:
        title = script.get("title") or script.get("topic") or "Untitled"
        lines = [f"Title: {title}", "Credit: Written by SuperDev AI", ""]
        text = script.get("text", "")
        for paragraph in text.split("\n"):
            paragraph = paragraph.strip()
            if not paragraph:
                lines.append("")
            elif paragraph.isupper():
                lines.append(paragraph)
            else:
                lines.append(f"> {paragraph}" if paragraph.endswith(":") else paragraph)
        return "\n".join(lines)

    def to_file(self, script: dict[str, Any], path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.export(script))


_fountain_export: FountainExport | None = None


def get_fountain_export() -> FountainExport:
    global _fountain_export
    if _fountain_export is None:
        _fountain_export = FountainExport()
    return _fountain_export
