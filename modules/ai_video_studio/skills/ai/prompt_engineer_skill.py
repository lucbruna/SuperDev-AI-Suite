"""Prompt engineer skill — optimized prompt construction."""
from __future__ import annotations
from typing import Any


class PromptEngineerSkill:
    """Craft a structured, role-and-context prompt for an LLM task."""

    skill_id = "prompt_engineer"
    skill_name = "Prompt Engineer"
    skill_version = "1.0.0"
    skill_description = "Build a structured LLM prompt: role, context, task, format."
    skill_category = "ai"
    skill_tags = ["ai", "prompt", "llm", "engineering"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        task: str,
        *,
        domain: str = "general",
        format: str = "markdown",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a composed prompt with explicit sections."""
        return {
            "task": task,
            "domain": domain,
            "language": language,
            "prompt": (
                f"You are an expert in {domain}.\n\n"
                f"Task: {task}.\n\n"
                f"Constraints:\n- Be concise and factual\n- Use {language}\n"
                f"- Output as {format}\n\n"
                f"Steps:\n1. Restate the goal\n2. Produce the deliverable\n3. List assumptions"
            ),
            "sections": ["role", "task", "constraints", "steps", "output_format"],
            "temperature_hint": 0.2,
        }
