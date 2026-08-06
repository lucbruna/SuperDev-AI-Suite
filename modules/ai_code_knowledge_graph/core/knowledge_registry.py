"""Knowledge registry — central component registry.

Scanners, parsers, analyzers, agents, workflows and plugins register here so
the pipeline and the API can discover and invoke them by name. Registration
is validated (duplicates raise) to keep the knowledge base deterministic.
"""
from __future__ import annotations

import logging
from typing import Any, Callable

from modules.ai_code_knowledge_graph.core.exceptions import KnowledgeError

logger = logging.getLogger(__name__)

_REGISTRY_KINDS = ("scanner", "parser", "analyzer", "agent", "workflow", "plugin")


class KnowledgeRegistry:
    """Name → component registry grouped by kind."""

    def __init__(self) -> None:
        self._components: dict[str, dict[str, Any]] = {kind: {} for kind in _REGISTRY_KINDS}

    def register(self, kind: str, name: str, component: Any, *, replace: bool = False) -> None:
        """Register a component under ``kind`` / ``name``."""
        if kind not in self._components:
            raise KnowledgeError(f"Unknown registry kind: {kind}", context={"kind": kind})
        if not name or not name.strip():
            raise KnowledgeError("Component name is required", context={"kind": kind})
        normalized = name.strip().lower()
        if normalized in self._components[kind] and not replace:
            raise KnowledgeError(
                f"Component '{name}' already registered for kind '{kind}'",
                context={"kind": kind, "name": name},
            )
        self._components[kind][normalized] = component
        logger.debug("Registered %s/%s", kind, name)

    def get(self, kind: str, name: str) -> Any:
        """Return a registered component or raise."""
        if kind not in self._components:
            raise KnowledgeError(f"Unknown registry kind: {kind}", context={"kind": kind})
        component = self._components[kind].get(name.strip().lower())
        if component is None:
            raise KnowledgeError(
                f"No {kind} named '{name}' is registered",
                context={"kind": kind, "name": name},
            )
        return component

    def all(self, kind: str) -> dict[str, Any]:
        """Return every registered component of a kind."""
        return dict(self._components.get(kind, {}))

    def names(self, kind: str) -> list[str]:
        """Return the sorted names of a kind."""
        return sorted(self._components.get(kind, {}))

    def counts(self) -> dict[str, int]:
        return {kind: len(components) for kind, components in self._components.items()}

    def has(self, kind: str, name: str) -> bool:
        return kind in self._components and name.strip().lower() in self._components[kind]

    def reset(self) -> None:
        self._components = {kind: {} for kind in _REGISTRY_KINDS}


def register_decorator(kind: str, name: str):
    """Decorator that registers a callable in a default registry."""

    def _decorate(fn: Callable) -> Callable:
        default_registry().register(kind, name, fn)
        return fn

    return _decorate


_DEFAULT_REGISTRY: KnowledgeRegistry | None = None


def default_registry() -> KnowledgeRegistry:
    """Return the process-wide default registry (singleton)."""
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = KnowledgeRegistry()
    return _DEFAULT_REGISTRY
