"""Example skill — hello world (echo)."""
from __future__ import annotations
from typing import Any


class HelloWorldSkill:
    """Minimal example skill: echoes the script back."""

    skill_id = "hello_world"
    skill_name = "Hello World"
    skill_version = "1.0.0"
    skill_description = "Minimal example skill that echoes its input."
    skill_category = "general"
    skill_tags = ["example", "hello"]
    skill_permissions: list[str] = []

    def __init__(self) -> None:
        pass

    async def __call__(self, script: str = "", **kwargs: Any) -> dict[str, Any]:
        return {"skill_id": self.skill_id, "echo": script, **kwargs}
