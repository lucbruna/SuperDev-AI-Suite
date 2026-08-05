"""SEO optimizer skill — on-page SEO plan for a topic or URL."""
from __future__ import annotations
from typing import Any


class SeoOptimizerSkill:
    """Produce an on-page SEO brief: keywords, title, meta, headings."""

    skill_id = "seo_optimizer"
    skill_name = "SEO Optimizer"
    skill_version = "1.0.0"
    skill_description = "On-page SEO brief (keywords, title, meta, heading outline) for a topic."
    skill_category = "marketing"
    skill_tags = ["marketing", "seo", "keywords", "content"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        topic: str,
        *,
        primary_keyword: str | None = None,
        language: str = "en",
    ) -> dict[str, Any]:
        """Return an SEO brief derived deterministically from the topic."""
        keyword = primary_keyword or topic.lower().replace(" ", "-")
        return {
            "topic": topic,
            "primary_keyword": keyword,
            "title_template": f"{topic}: A Practical Guide",
            "meta_description": f"Everything you need to know about {topic}, explained simply.",
            "url_slug": keyword,
            "headings": [
                {"tag": "H1", "content": topic},
                {"tag": "H2", "content": f"Why {topic} matters"},
                {"tag": "H2", "content": f"How to get started with {topic}"},
                {"tag": "H3", "content": f"Common mistakes with {topic}"},
            ],
            "language": language,
            "word_count_target": 1500,
        }
