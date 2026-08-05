"""Script generator — produces the main body script from a brief."""
from __future__ import annotations

from typing import Any


class ScriptGenerator:
    """Generates a full script body with sections."""

    def generate(self, brief: str, tone: str = "informative", duration: float = 30.0) -> dict[str, Any]:
        words_target = int(duration / 60 * 150)
        intro = f"Hoje vamos falar sobre {brief.lower() or 'o tema de hoje'}."
        body = f"Primeiro, entendemos o essencial de {brief.lower() or 'o assunto'}. Depois aplicamos na prática."
        outro = "Se este conteúdo foi útil, acompanhe os próximos vídeos."
        text = f"{intro} {body} {outro}"
        return {
            "text": text,
            "words": len(text.split()),
            "words_target": words_target,
            "tone": tone,
            "sections": ["intro", "body", "outro"],
            "duration_est": len(text.split()) / 150 * 60,
        }


_script_generator: ScriptGenerator | None = None


def get_script_generator() -> ScriptGenerator:
    global _script_generator
    if _script_generator is None:
        _script_generator = ScriptGenerator()
    return _script_generator
