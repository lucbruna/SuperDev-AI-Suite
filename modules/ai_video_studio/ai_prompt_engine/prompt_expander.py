"""Prompt expander — expand prompts with structure and detail."""
from __future__ import annotations

from typing import Any

SECTIONS = ("intro", "main", "outro")


class PromptExpander:
    """Expands a brief into a structured, detailed prompt."""

    def expand(self, prompt: str, sections: int = 3) -> dict[str, Any]:
        text = (prompt or "").strip().rstrip(".")
        if not text:
            return {"original": prompt, "expanded": "", "sections": []}

        n = max(1, min(sections, len(SECTIONS)))
        parts: list[str] = []
        for i in range(n):
            label = SECTIONS[i] if i < len(SECTIONS) else f"section_{i + 1}"
            parts.append(f"{label}: {text} — {self._section_hint(label)}")

        expanded = (
            f"Video brief: {text}.\n"
            + "\n".join(f"- {p}" for p in parts)
            + "\nInclude clear visuals, professional narration and a strong call to action."
        )
        return {"original": prompt, "expanded": expanded, "sections": [p for p in parts]}

    def expand_for_scene(self, prompt: str, scene_index: int) -> str:
        text = (prompt or "").strip().rstrip(".")
        return (
            f"Scene {scene_index + 1}: {text}. "
            "Describe the setting, subject, action, camera movement and mood in detail."
        )

    @staticmethod
    def _section_hint(label: str) -> str:
        hints = {
            "intro": "hook the audience and state the topic",
            "main": "develop the key points with examples",
            "outro": "summarize and give a call to action",
        }
        return hints.get(label, "continue the narrative")


_prompt_expander: PromptExpander | None = None


def get_prompt_expander() -> PromptExpander:
    global _prompt_expander
    if _prompt_expander is None:
        _prompt_expander = PromptExpander()
    return _prompt_expander
