"""Deterministic prompt templates for the autonomous developer."""
from __future__ import annotations

from dataclasses import dataclass

__all__ = ["PromptError", "PromptLibrary", "PromptTemplate"]


class PromptError(ValueError):
    """Raised for unknown templates or missing variables."""


@dataclass(slots=True)
class PromptTemplate:
    """A named, versioned prompt template with declared variables."""

    name: str
    template: str
    variables: tuple[str, ...]


class PromptLibrary:
    """Holds named prompt templates and renders them with keyword args.

    Rendering is plain ``str.format``: unknown variables render as-is and
    missing variables raise :class:`PromptError`.
    """

    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplate] = {
            "system": PromptTemplate(
                "system",
                "You are the {role}. Stay deterministic and precise.",
                ("role",),
            ),
            "plan": PromptTemplate(
                "plan",
                "Decompose the goal into small, verifiable tasks.\nGoal: {goal}",
                ("goal",),
            ),
            "implement": PromptTemplate(
                "implement",
                "Implement the task titled '{title}'.",
                ("title",),
            ),
            "review": PromptTemplate(
                "review",
                "Review {count} file change(s) and return a verdict.",
                ("count",),
            ),
            "test": PromptTemplate(
                "test",
                "Generate a pytest module for '{module}'.",
                ("module",),
            ),
        }

    def names(self) -> list[str]:
        """All registered template names, in registration order."""
        return list(self._templates)

    def template(self, name: str) -> PromptTemplate:
        """Fetch a template by name; raises :class:`PromptError` if unknown."""
        try:
            return self._templates[name]
        except KeyError:
            raise PromptError(f"Unknown prompt template: {name!r}") from None

    def render(self, name: str, **kwargs: object) -> str:
        """Render a named template with the given variables."""
        tmpl = self.template(name)
        try:
            return tmpl.template.format(**kwargs)
        except KeyError as exc:
            raise PromptError(
                f"Missing variable {exc} for prompt template {name!r}"
            ) from None
