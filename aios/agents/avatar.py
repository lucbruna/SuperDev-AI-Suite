"""AvatarAgent: deterministic avatar and persona configuration."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent

AVATAR_STYLES = ("realistic", "cartoon", "minimal", "pixel")


class AvatarAgent(BaseAgent):
    def __init__(self, name: str = "avatar", **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="avatar",
            capabilities=["avatar_generation", "persona_design", "motion"],
            description="Designs avatars and motion sets",
            **kwargs,
        )

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        persona = input_data if isinstance(input_data, str) else str(input_data.get("persona", "assistant"))
        if isinstance(input_data, dict):
            style = input_data.get("style") or context.get("style", "realistic")
        else:
            style = context.get("style", "realistic")
        if style not in AVATAR_STYLES:
            style = AVATAR_STYLES[0]
        expressions = ["neutral", "happy", "thinking"]
        return {
            "persona": persona,
            "style": style,
            "expressions": expressions,
            "motion_set": ["idle", "wave", "talk"],
            "config": {"persona": persona, "style": style, "expressions": expressions},
            "recommendation": f"start with {style} style for {persona}",
        }
