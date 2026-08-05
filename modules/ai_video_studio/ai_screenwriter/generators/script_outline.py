"""Script outline generator — produces a structured outline."""
from __future__ import annotations

from typing import Any


class ScriptOutline:
    """Generates a structured outline for the script."""

    def generate(self, brief: str, sections: int = 3) -> dict[str, Any]:
        base = brief or "tema"
        return {
            "sections": [f"{i + 1}. {base} — parte {i + 1}" for i in range(sections)],
            "structure": "intro-body-outro",
        }


_script_outline: ScriptOutline | None = None


def get_script_outline() -> ScriptOutline:
    global _script_outline
    if _script_outline is None:
        _script_outline = ScriptOutline()
    return _script_outline
