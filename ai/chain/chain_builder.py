from __future__ import annotations

from typing import Any


class ChainBuilder:
    """Builds reasoning chains from context and objectives."""

    def __init__(self) -> None:
        self._templates: dict[str, list[dict[str, Any]]] = {}

    def register_template(self, name: str, steps: list[dict[str, Any]]) -> None:
        self._templates[name] = steps

    async def build(self, context: dict[str, Any]) -> dict[str, Any]:
        complexity = context.get("complexity", "low")
        template_name = context.get("template", "default")
        if template_name in self._templates:
            steps = self._templates[template_name]
        else:
            if complexity == "high":
                steps = [
                    {"id": "analyze", "type": "analyze", "description": "Analyze the problem"},
                    {"id": "decompose", "type": "decompose", "description": "Break down into sub-problems"},
                    {"id": "reason", "type": "reason", "description": "Apply reasoning to each part"},
                    {"id": "synthesize", "type": "synthesize", "description": "Combine results"},
                ]
            elif complexity == "medium":
                steps = [
                    {"id": "reason", "type": "reason", "description": "Apply reasoning"},
                    {"id": "conclude", "type": "conclude", "description": "Draw conclusion"},
                ]
            else:
                steps = [{"id": "reason", "type": "reason", "description": "Simple reasoning step"}]
        return {"steps": steps, "complexity": complexity, "template": template_name}
