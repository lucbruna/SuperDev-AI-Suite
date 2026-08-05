"""LinkedIn Content — post and article generation (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_TEMPLATES = {
    "insight": "In our latest work on {topic}, one insight stood out: {insight}. What has your experience been?",
    "tip": "Quick tip on {topic}: {tip}. Save this for later.",
    "question": "Polling the network: what is the biggest {topic} challenge you face today?",
}


class LinkedInContent:
    """Generate LinkedIn post drafts and content ideas."""

    def draft(self, *, template: str = "insight", topic: str = "", **kwargs) -> dict:
        """Build a post draft from a named template."""
        body = _TEMPLATES.get(template, _TEMPLATES["insight"])
        rendered = body.format(topic=topic or "your industry", **kwargs)
        return {
            "template": template,
            "body": rendered,
            "character_count": len(rendered),
            "suggested_length": "ok" if 150 <= len(rendered) <= 3000 else "review",
        }

    def ideas(self, *, topics: list[str] | None = None, count: int = 5) -> dict:
        """Generate a list of content ideas from seed topics."""
        seeds = topics or ["thought leadership", "industry news", "lessons learned"]
        ideas = [f"Post about {seed} with a personal story" for seed in seeds]
        return {"ideas": ideas[:count], "count": min(count, len(ideas))}

    def stats(self) -> dict[str, int]:
        return {"templates": len(_TEMPLATES)}


_CONTENT: LinkedInContent | None = None


def get_linkedin_content() -> LinkedInContent:
    """Get the module-level singleton LinkedIn content generator."""
    global _CONTENT
    if _CONTENT is None:
        _CONTENT = LinkedInContent()
    return _CONTENT
