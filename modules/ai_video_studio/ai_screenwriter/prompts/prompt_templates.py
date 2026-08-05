"""Prompt templates — reusable prompt strings per purpose."""
from __future__ import annotations


TEMPLATES = {
    "script": "Roteiro completo sobre: {brief}",
    "hook": "Abertura impactante para vídeo sobre: {brief}",
    "title": "Títulos chamativos para vídeo sobre: {brief}",
    "outline": "Estrutura para roteiro sobre: {brief}",
    "review": "Revise este roteiro: {brief}",
}


class PromptTemplates:
    """Provides prompt templates by purpose."""

    def get(self, purpose: str) -> str:
        return TEMPLATES.get(purpose, TEMPLATES["script"])

    def render(self, purpose: str, brief: str) -> str:
        return self.get(purpose).format(brief=brief)


_prompt_templates: PromptTemplates | None = None


def get_prompt_templates() -> PromptTemplates:
    global _prompt_templates
    if _prompt_templates is None:
        _prompt_templates = PromptTemplates()
    return _prompt_templates
