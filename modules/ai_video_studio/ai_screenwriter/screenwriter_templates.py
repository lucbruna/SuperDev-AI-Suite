"""Screenwriter templates — reusable script structures."""
from __future__ import annotations



class ScreenwriterTemplates:
    """Provides reusable script templates by format."""

    TEMPLATES = {
        "youtube": ["hook", "intro", "body", "cta", "outro"],
        "tiktok": ["hook", "value", "cta"],
        "instagram": ["hook", "story", "cta"],
        "linkedin": ["hook", "insight", "call"],
        "ad": ["problem", "solution", "proof", "cta"],
        "tutorial": ["intro", "steps", "summary"],
    }

    def get(self, format_name: str) -> list[str]:
        return self.TEMPLATES.get(format_name, self.TEMPLATES["youtube"])

    def list_formats(self) -> list[str]:
        return list(self.TEMPLATES.keys())


_screenwriter_templates: ScreenwriterTemplates | None = None


def get_screenwriter_templates() -> ScreenwriterTemplates:
    global _screenwriter_templates
    if _screenwriter_templates is None:
        _screenwriter_templates = ScreenwriterTemplates()
    return _screenwriter_templates
