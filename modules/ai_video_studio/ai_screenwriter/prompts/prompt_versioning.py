"""Prompt versioning — tracks versions of prompt templates."""
from __future__ import annotations



class PromptVersioning:
    """Keeps version history of prompt templates."""

    def __init__(self) -> None:
        self._versions: dict[str, list[str]] = {}

    def add(self, purpose: str, template: str) -> int:
        history = self._versions.setdefault(purpose, [])
        history.append(template)
        return len(history)

    def latest(self, purpose: str) -> str | None:
        history = self._versions.get(purpose)
        return history[-1] if history else None

    def history(self, purpose: str) -> list[str]:
        return list(self._versions.get(purpose, []))


_prompt_versioning: PromptVersioning | None = None


def get_prompt_versioning() -> PromptVersioning:
    global _prompt_versioning
    if _prompt_versioning is None:
        _prompt_versioning = PromptVersioning()
    return _prompt_versioning
