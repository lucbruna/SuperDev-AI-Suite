"""Doc writer skill — documentation plan for a component."""
from __future__ import annotations
from typing import Any


class DocWriterSkill:
    """Plan documentation: README, API docs, and usage examples."""

    skill_id = "doc_writer"
    skill_name = "Doc Writer"
    skill_version = "1.0.0"
    skill_description = "Documentation plan: README, API reference, examples, FAQ."
    skill_category = "development"
    skill_tags = ["development", "documentation", "readme", "writing"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        project: str,
        *,
        audience: str = "developers",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a documentation outline for the project."""
        return {
            "project": project,
            "audience": audience,
            "language": language,
            "documents": [
                {"doc": "README", "sections": ["what it does", "quick start", "examples", "license"]},
                {"doc": "Getting Started", "sections": ["installation", "first steps", "troubleshooting"]},
                {"doc": "API Reference", "sections": ["endpoints or functions", "parameters", "errors"]},
                {"doc": "Contributing", "sections": ["setup", "style", "test commands", "PR process"]},
                {"doc": "FAQ", "sections": ["common questions", "workarounds"]},
            ],
            "style": "short sentences, concrete examples, one idea per section",
        }
