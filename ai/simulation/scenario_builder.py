from __future__ import annotations

from typing import Any


class ScenarioBuilder:
    """Builds simulation scenarios from context."""

    def __init__(self) -> None:
        self._templates: dict[str, dict[str, Any]] = {}

    def register_template(self, name: str, template: dict[str, Any]) -> None:
        self._templates[name] = template

    async def build(self, context: dict[str, Any]) -> dict[str, Any]:
        template_name = context.get("template", "default")
        if template_name in self._templates:
            base = dict(self._templates[template_name])
        else:
            base = {
                "name": context.get("name", "default_scenario"),
                "steps": context.get("steps", []),
                "resources": context.get("resources", {"cpu": 1, "memory": 512}),
                "constraints": context.get("constraints", {}),
            }
        base.update({k: v for k, v in context.items() if k not in base})
        return base

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.build(context)
