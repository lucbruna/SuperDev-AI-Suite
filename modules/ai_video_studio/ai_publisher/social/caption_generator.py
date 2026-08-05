"""Caption Generator — template + style-based social captions (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_TEMPLATES = [
    "{hook} — {body} {cta}",
    "Você sabia? {body} {cta}",
    "Não vai querer perder: {body} {cta}",
    "Guarda esse post: {body} {cta}",
    "{hook}\n\n{body}\n\n{cta}",
]


class CaptionGenerator:
    """Generate captions from topic/hook with configurable tone and length."""

    def generate(
        self,
        *,
        topic: str,
        hook: str = "",
        tone: str = "casual",
        max_chars: int = 280,
    ) -> dict:
        """Build one caption from templates with tone adjustments."""
        hook_text = hook or topic
        body = self._body(topic, tone)
        cta = self._cta(tone)
        caption = ""
        for template in _TEMPLATES:
            candidate = template.format(hook=hook_text, body=body, cta=cta)
            if len(candidate) <= max_chars:
                caption = candidate
                break
        if not caption:
            caption = f"{hook_text} — {body} {cta}"[:max_chars].rsplit(" ", 1)[0] + "…"
        return {
            "caption": caption,
            "tone": tone,
            "length": len(caption),
            "max_chars": max_chars,
        }

    @staticmethod
    def _body(topic: str, tone: str) -> str:
        if tone == "professional":
            return f"Um guia direto sobre {topic.lower()} — insights práticos e objetivos."
        if tone == "fun":
            return f"Bora falar de {topic.lower()} de um jeito leve e divertido!"
        return f"Aqui vai tudo o que você precisa saber sobre {topic.lower()}."

    @staticmethod
    def _cta(tone: str) -> str:
        if tone == "professional":
            return "Compartilhe com quem precisa ver. 💼"
        if tone == "fun":
            return "Curtiu? Manda pra um amigo! 🚀"
        return "Comenta aí o que você achou! 👇"

    def stats(self) -> dict[str, int]:
        return {"templates": len(_TEMPLATES)}


_GENERATOR: CaptionGenerator | None = None


def get_caption_generator() -> CaptionGenerator:
    """Get the module-level singleton caption generator."""
    global _GENERATOR
    if _GENERATOR is None:
        _GENERATOR = CaptionGenerator()
    return _GENERATOR
