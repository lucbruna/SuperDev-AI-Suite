"""Hook generator — creates attention-grabbing opening lines."""
from __future__ import annotations


class HookGenerator:
    """Generates a hook line for the script."""

    def generate(self, brief: str) -> str:
        if not brief:
            return "Você sabia disso?"
        return f"Você sabia que {brief.lower()} pode transformar o seu resultado?"


_hook_generator: HookGenerator | None = None


def get_hook_generator() -> HookGenerator:
    global _hook_generator
    if _hook_generator is None:
        _hook_generator = HookGenerator()
    return _hook_generator
