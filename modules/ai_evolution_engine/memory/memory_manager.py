"""Memory manager: layered deterministic memory over EvolutionMemory."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_memory import EvolutionMemory


class MemoryManager:
    """Wraps EvolutionMemory with short/long-term namespacing."""

    def __init__(self, memory: EvolutionMemory | None = None) -> None:
        self._memory = memory or EvolutionMemory()

    def store(self, key: str, value: object, namespace: str = "default") -> None:
        self._memory.remember(f"{namespace}:{key}", value)

    def load(self, key: str, namespace: str = "default", default: object = None) -> object:
        return self._memory.recall(f"{namespace}:{key}", default)

    def snapshot(self, namespace: str = "default") -> dict[str, object]:
        prefix = f"{namespace}:"
        return {
            key[len(prefix):]: value
            for key, value in self._memory.entries().items()
            if key.startswith(prefix)
        }

    def clear_namespace(self, namespace: str) -> None:
        prefix = f"{namespace}:"
        for key in list(self._memory.entries()):
            if key.startswith(prefix):
                self._memory.forget(key)
