"""DeveloperAgent: deterministic code generation from structured specs."""
from __future__ import annotations

from typing import Any

from aios.agents.base_agent import BaseAgent

LANGUAGE_TEMPLATES: dict[str, str] = {
    "python": "def {name}({params}):\n    {body}\n",
    "javascript": "function {name}({params}) {{\n  {body}\n}}\n",
    "typescript": "export function {name}({params}): {ret} {{\n  {body}\n}}\n",
    "sql": "SELECT * FROM {name} WHERE {params};\n",
}


class DeveloperAgent(BaseAgent):
    def __init__(self, name: str = "developer", templates: dict[str, str] | None = None, **kwargs: Any) -> None:
        super().__init__(
            name=name,
            role="developer",
            capabilities=["code_generation", "refactoring", "code_review"],
            description="Generates and reviews code",
            **kwargs,
        )
        self.templates = dict(templates or LANGUAGE_TEMPLATES)

    def process(self, input_data: Any, context: dict[str, Any]) -> Any:
        if isinstance(input_data, dict):
            spec = dict(input_data)
        else:
            spec = {"name": str(input_data), "language": context.get("language", "python")}
        language = spec.get("language", "python")
        name = spec.get("name", "main")
        params = ", ".join(spec.get("params", ["arg"]))
        body = spec.get("body", "pass" if language == "python" else "// TODO: implement")
        template = self.templates.get(language, self.templates["python"])
        code = template.format(name=name, params=params, body=body, ret=spec.get("return_type", "void"))
        return {
            "language": language,
            "function": name,
            "code": code,
            "lines": len(code.splitlines()),
            "suggestions": [f"add unit tests for {name}", "document the public API"],
        }
