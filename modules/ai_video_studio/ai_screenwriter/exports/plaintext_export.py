"""Plaintext export — renders a script as readable plain text."""
from __future__ import annotations

from typing import Any


class PlaintextExport:
    """Exports a script to plain text with section headers."""

    def export(self, script: dict[str, Any]) -> str:
        title = script.get("title") or script.get("topic") or "Untitled"
        lines = [title.upper(), "=" * len(title), ""]
        text = script.get("text", "")
        lines.append(text)
        review = script.get("review")
        if review:
            lines.extend(["", "Review:", f"  Score: {review.get('score', 0.0)}"])
            for issue in review.get("issues", []):
                lines.append(f"  - {issue}")
        return "\n".join(lines)

    def to_file(self, script: dict[str, Any], path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.export(script))


_plaintext_export: PlaintextExport | None = None


def get_plaintext_export() -> PlaintextExport:
    global _plaintext_export
    if _plaintext_export is None:
        _plaintext_export = PlaintextExport()
    return _plaintext_export
