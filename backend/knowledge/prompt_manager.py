from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PromptTemplate:
    name: str
    template: str
    description: str = ""
    variables: list[str] = field(default_factory=list)
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    tags: list[str] = field(default_factory=list)

    def render(self, **kwargs: Any) -> str:
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "template": self.template,
            "description": self.description,
            "variables": self.variables,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PromptTemplate:
        return cls(**data)


class PromptManager:
    """Manages prompt templates for LLM interactions."""

    def __init__(self, storage_path: str | Path | None = None):
        self._templates: dict[str, PromptTemplate] = {}
        self._storage_path = Path(storage_path) if storage_path else None
        if self._storage_path and self._storage_path.exists():
            self._load_templates()

    def _load_templates(self) -> None:
        if not self._storage_path:
            return
        for file in self._storage_path.glob("*.json"):
            with open(file) as f:
                data = json.load(f)
                template = PromptTemplate.from_dict(data)
                self._templates[template.name] = template

    def _save_template(self, template: PromptTemplate) -> None:
        if not self._storage_path:
            return
        self._storage_path.mkdir(parents=True, exist_ok=True)
        file_path = self._storage_path / f"{template.name}.json"
        with open(file_path, "w") as f:
            json.dump(template.to_dict(), f, indent=2)

    def register(self, template: PromptTemplate) -> None:
        self._templates[template.name] = template
        self._save_template(template)

    def get(self, name: str) -> PromptTemplate | None:
        return self._templates.get(name)

    def render(self, name: str, **kwargs: Any) -> str:
        template = self._templates.get(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
        return template.render(**kwargs)

    def list_templates(self, tag: str | None = None) -> list[PromptTemplate]:
        templates = list(self._templates.values())
        if tag:
            templates = [t for t in templates if tag in t.tags]
        return templates

    def delete(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            if self._storage_path:
                file_path = self._storage_path / f"{name}.json"
                if file_path.exists():
                    file_path.unlink()
            return True
        return False

    def update(self, name: str, **kwargs: Any) -> PromptTemplate | None:
        template = self._templates.get(name)
        if not template:
            return None
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        self._save_template(template)
        return template


BUILTIN_PROMPTS = [
    PromptTemplate(
        name="code_review",
        template="Review the following code and provide feedback on:\n1. Code quality\n2. Potential bugs\n3. Performance improvements\n4. Security concerns\n\nCode:\n```{language}\n{code}\n```",
        description="Code review prompt",
        variables=["language", "code"],
        tags=["code", "review"],
    ),
    PromptTemplate(
        name="code_explanation",
        template="Explain the following code in detail. Include:\n1. What it does\n2. How it works\n3. Key concepts used\n\nCode:\n```{language}\n{code}\n```",
        description="Code explanation prompt",
        variables=["language", "code"],
        tags=["code", "explain"],
    ),
    PromptTemplate(
        name="bug_fix",
        template="I have the following bug in my code:\n\nError: {error}\n\nCode:\n```{language}\n{code}\n```\n\nPlease identify the issue and provide a fix.",
        description="Bug fix prompt",
        variables=["error", "language", "code"],
        tags=["code", "debug"],
    ),
    PromptTemplate(
        name="documentation",
        template="Generate comprehensive documentation for the following code:\n\n```{language}\n{code}\n```\n\nInclude:\n1. Module/function description\n2. Parameters\n3. Return values\n4. Usage examples\n5. Edge cases",
        description="Documentation generation prompt",
        variables=["language", "code"],
        tags=["code", "docs"],
    ),
    PromptTemplate(
        name="test_generation",
        template="Generate unit tests for the following code:\n\n```{language}\n{code}\n```\n\nRequirements:\n- Use {test_framework}\n- Cover edge cases\n- Include assertions\n- Follow AAA pattern",
        description="Test generation prompt",
        variables=["language", "code", "test_framework"],
        tags=["code", "test"],
    ),
    PromptTemplate(
        name="refactor",
        template="Refactor the following code to improve:\n1. Readability\n2. Performance\n3. Maintainability\n\nOriginal code:\n```{language}\n{code}\n```\n\n{additional_requirements}",
        description="Code refactoring prompt",
        variables=["language", "code", "additional_requirements"],
        tags=["code", "refactor"],
    ),
]


prompt_manager = PromptManager()
for prompt in BUILTIN_PROMPTS:
    prompt_manager.register(prompt)
